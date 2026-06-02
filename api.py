from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db
from repository import BolgeRepository, AfetOlayiRepository, TahminRepository
from model_singleton import AIModelSingleton
from gemini_service import GeminiService

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Tüm domainlerden gelen isteklere izin ver

# Bulut ortamında DATABASE_URL environment variable'dan okunur
# Lokal geliştirmede SQLite kullanılır
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///afet_verileri.db')
# Supabase/Render bazen "postgres://" prefix'i verir, SQLAlchemy "postgresql://" ister
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)

model_singleton = AIModelSingleton()

# Gemini API servisi başlat
try:
    gemini_service = GeminiService()
    print("Gemini API servisi başarıyla başlatıldı.")
except Exception as e:
    gemini_service = None
    print(f"Gemini API servisi başlatılamadı: {e}")


@app.route('/bolge', methods=['POST'])
def bolge_ekle():
    veri = request.get_json()
    gerekli = ['ad', 'il', 'nufus']
    for alan in gerekli:
        if alan not in veri:
            return jsonify({'status': 'error', 'message': f'Eksik parametre: {alan}'}), 400

    bolge_id = BolgeRepository.kaydet(
        ad=veri['ad'],
        il=veri['il'],
        nufus=veri['nufus'],
        ilce=veri.get('ilce'),
        lat=veri.get('koordinat_lat'),
        lon=veri.get('koordinat_lon'),
    )
    return jsonify({'status': 'success', 'bolge_id': bolge_id}), 201


@app.route('/bolge', methods=['GET'])
def bolgeleri_listele():
    bolgeler = BolgeRepository.hepsini_getir()
    return jsonify([
        {'id': b.id, 'ad': b.ad, 'il': b.il, 'ilce': b.ilce, 'nufus': b.nufus}
        for b in bolgeler
    ]), 200


@app.route('/predict', methods=['POST'])
def predict():
    try:
        veri = request.get_json()

        gerekli_alanlar = [
            'bolge_id', 'deprem_buyuklugu', 'bina_yikim_orani',
            'hava_sicakligi', 'ulasim_durumu', 'yasli_nufus_orani'
        ]
        for alan in gerekli_alanlar:
            if alan not in veri:
                return jsonify({'status': 'error', 'message': f'Eksik parametre: {alan}'}), 400

        bolge = BolgeRepository.id_ile_getir(veri['bolge_id'])
        if bolge is None:
            return jsonify({'status': 'error', 'message': 'Bolge bulunamadi'}), 404

        afet_olayi_id = AfetOlayiRepository.kaydet(veri['bolge_id'], veri)

        tahmin_verisi = {
            'nufus': bolge.nufus,
            'deprem_buyuklugu': veri['deprem_buyuklugu'],
            'bina_yikim_orani': veri['bina_yikim_orani'],
            'hava_sicakligi': veri['hava_sicakligi'],
            'ulasim_durumu': veri['ulasim_durumu'],
            'yasli_nufus_orani': veri['yasli_nufus_orani'],
        }
        # İş Kuralı (Business Logic): Eğer bina yıkımı %0 ise veya deprem 3.5'tan küçükse
        # acil bir kriz durumu yoktur, yapay zeka istatistiğine gerek kalmadan 0 döndürülür.
        if veri['bina_yikim_orani'] <= 0.0 or veri['deprem_buyuklugu'] < 3.5:
            tahmin = [0, 0, 0, 0, 0]
        else:
            # Makine öğrenmesi tahmini
            tahmin = model_singleton.predict(tahmin_verisi)

        kayit_id = TahminRepository.kaydet(afet_olayi_id, tahmin)

        # AI Kısa Değerlendirme Özeti
        ai_ozet = "Yapay zekâ özeti şu an oluşturulamadı."
        if gemini_service is not None:
            try:
                ai_ozet = gemini_service.kisa_degerlendirme_olustur(bolge, tahmin)
            except Exception as e:
                print(f"AI Özet Hatası: {e}")
                ai_ozet = "⚠️ Gemini Yapay Zeka kotası şu an dolu. Lütfen 1 dakika bekleyip tekrar deneyin."

        return jsonify({
            'status': 'success',
            'kayit_id': kayit_id,
            'afet_olayi_id': afet_olayi_id,
            'bolge': {'id': bolge.id, 'ad': bolge.ad, 'il': bolge.il},
            'sonuclar': {
                'acil_barinma': int(tahmin[0]),
                'gida': int(tahmin[1]),
                'su': int(tahmin[2]),
                'medikal': int(tahmin[3]),
                'ekip': int(tahmin[4])
            },
            'ai_ozet': ai_ozet
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/tahminler/<int:afet_olayi_id>', methods=['GET'])
def tahminleri_getir(afet_olayi_id):
    kayitlar = TahminRepository.olay_id_ile_getir(afet_olayi_id)
    if not kayitlar:
        return jsonify({'status': 'error', 'message': 'Tahmin bulunamadi'}), 404
    return jsonify([
        {
            'id': k.id,
            'acil_barinma': k.acil_barinma,
            'gida': k.gida,
            'su': k.su,
            'medikal': k.medikal,
            'ekip': k.ekip,
            'kayit_tarihi': k.kayit_tarihi.isoformat()
        }
        for k in kayitlar
    ]), 200


# ==================== Gemini AI Endpoint'leri ====================

@app.route('/ai/analiz', methods=['POST'])
def ai_analiz():
    """
    Belirli bir afet olayının tahmin sonuçlarını Gemini API ile analiz ederek
    kapsamlı bir durum raporu üretir.

    Request JSON:
        {"afet_olayi_id": int}

    Response:
        {"status": "success", "analiz_raporu": str, "bolge": dict, "tahmin": dict}
    """
    if gemini_service is None:
        return jsonify({'status': 'error', 'message': 'Gemini API servisi kullanılamıyor.'}), 503

    try:
        veri = request.get_json()
        if not veri or 'afet_olayi_id' not in veri:
            return jsonify({'status': 'error', 'message': 'Eksik parametre: afet_olayi_id'}), 400

        afet_olayi_id = veri['afet_olayi_id']

        # Afet olayını getir
        afet_olayi = AfetOlayiRepository.id_ile_getir(afet_olayi_id)
        if afet_olayi is None:
            return jsonify({'status': 'error', 'message': 'Afet olayı bulunamadı.'}), 404

        # Bölge bilgisini getir
        bolge = BolgeRepository.id_ile_getir(afet_olayi.bolge_id)
        if bolge is None:
            return jsonify({'status': 'error', 'message': 'Bölge bulunamadı.'}), 404

        # En son tahmin kaydını getir
        tahmin = TahminRepository.son_tahmin_getir(afet_olayi_id)
        if tahmin is None:
            return jsonify({'status': 'error', 'message': 'Tahmin kaydı bulunamadı.'}), 404

        # Gemini ile analiz raporu oluştur
        try:
            rapor = gemini_service.analiz_raporu_olustur(bolge, tahmin, afet_olayi)
        except Exception:
            rapor = f"""
## ⚠️ Yapay Zeka Servisi (Gemini) Geçici Olarak Kullanılamıyor

Şu anda yapay zeka servisinin ücretsiz kullanım limiti (dakika başı istek kotası) dolmuştur. Detaylı doğal dil analizi üretilememektedir. Ancak makine öğrenmesi tahminlerimiz güvendedir.

### 📊 Elde Edilen Sayısal Tahminler:
- **Acil Barınma:** {tahmin.acil_barinma:,} Çadır/Konteyner
- **Gıda:** {tahmin.gida:,} Öğün
- **Su:** {tahmin.su:,} Litre
- **Medikal Kit:** {tahmin.medikal:,} Adet
- **Arama Kurtarma:** {tahmin.ekip:,} Ekip

*Lütfen API kotasının sıfırlanması için yaklaşık 1 dakika bekleyip raporu tekrar üretmeyi deneyin.*
"""

        return jsonify({
            'status': 'success',
            'analiz_raporu': rapor,
            'bolge': {
                'id': bolge.id,
                'ad': bolge.ad,
                'il': bolge.il,
                'ilce': bolge.ilce,
                'nufus': bolge.nufus
            },
            'tahmin': {
                'acil_barinma': tahmin.acil_barinma,
                'gida': tahmin.gida,
                'su': tahmin.su,
                'medikal': tahmin.medikal,
                'ekip': tahmin.ekip
            }
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Sunucu Hatası: {str(e)}'}), 500


@app.route('/ai/ozetle', methods=['POST'])
def ai_ozetle():
    """
    Bir bölgedeki birden fazla afet olayının tahmin sonuçlarını
    Gemini API ile özetleyerek karşılaştırmalı analiz yapar.

    Request JSON:
        {"bolge_id": int}

    Response:
        {"status": "success", "ozet_raporu": str, "bolge": dict, "tahmin_sayisi": int}
    """
    if gemini_service is None:
        return jsonify({'status': 'error', 'message': 'Gemini API servisi kullanılamıyor.'}), 503

    try:
        veri = request.get_json()
        if not veri or 'bolge_id' not in veri:
            return jsonify({'status': 'error', 'message': 'Eksik parametre: bolge_id'}), 400

        bolge_id = veri['bolge_id']

        # Bölgeyi getir
        bolge = BolgeRepository.id_ile_getir(bolge_id)
        if bolge is None:
            return jsonify({'status': 'error', 'message': 'Bölge bulunamadı.'}), 404

        # Bölgeye ait tüm tahminleri getir
        tahminler = TahminRepository.bolge_tahminlerini_getir(bolge_id)
        if not tahminler:
            return jsonify({'status': 'error', 'message': 'Bu bölgeye ait tahmin kaydı bulunamadı.'}), 404

        # Gemini ile özet oluştur
        ozet = gemini_service.tahminleri_ozetle(bolge, tahminler)

        return jsonify({
            'status': 'success',
            'ozet_raporu': ozet,
            'bolge': {
                'id': bolge.id,
                'ad': bolge.ad,
                'il': bolge.il,
                'nufus': bolge.nufus
            },
            'tahmin_sayisi': len(tahminler)
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Gemini API hatası: {str(e)}'}), 500


@app.route('/ai/oneri', methods=['POST'])
def ai_oneri():
    """
    Belirli bir afet olayının tahmin sonuçlarına dayanarak
    Gemini API ile detaylı lojistik ve kaynak dağıtım önerileri üretir.

    Request JSON:
        {"afet_olayi_id": int}

    Response:
        {"status": "success", "lojistik_onerisi": str, "bolge": dict, "tahmin": dict}
    """
    if gemini_service is None:
        return jsonify({'status': 'error', 'message': 'Gemini API servisi kullanılamıyor.'}), 503

    try:
        veri = request.get_json()
        if not veri or 'afet_olayi_id' not in veri:
            return jsonify({'status': 'error', 'message': 'Eksik parametre: afet_olayi_id'}), 400

        afet_olayi_id = veri['afet_olayi_id']

        # Afet olayını getir
        afet_olayi = AfetOlayiRepository.id_ile_getir(afet_olayi_id)
        if afet_olayi is None:
            return jsonify({'status': 'error', 'message': 'Afet olayı bulunamadı.'}), 404

        # Bölge bilgisini getir
        bolge = BolgeRepository.id_ile_getir(afet_olayi.bolge_id)
        if bolge is None:
            return jsonify({'status': 'error', 'message': 'Bölge bulunamadı.'}), 404

        # En son tahmin kaydını getir
        tahmin = TahminRepository.son_tahmin_getir(afet_olayi_id)
        if tahmin is None:
            return jsonify({'status': 'error', 'message': 'Tahmin kaydı bulunamadı.'}), 404

        # Gemini ile lojistik önerisi oluştur
        oneri = gemini_service.lojistik_onerisi_olustur(bolge, tahmin, afet_olayi)

        return jsonify({
            'status': 'success',
            'lojistik_onerisi': oneri,
            'bolge': {
                'id': bolge.id,
                'ad': bolge.ad,
                'il': bolge.il,
                'nufus': bolge.nufus
            },
            'tahmin': {
                'acil_barinma': tahmin.acil_barinma,
                'gida': tahmin.gida,
                'su': tahmin.su,
                'medikal': tahmin.medikal,
                'ekip': tahmin.ekip
            }
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Gemini API hatası: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
