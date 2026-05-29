from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db
from repository import BolgeRepository, AfetOlayiRepository, TahminRepository
from model_singleton import AIModelSingleton

import os

app = Flask(__name__)

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
            'bina_yikim_orani': veri['bina_yikim_orani'],
            'hava_sicakligi': veri['hava_sicakligi'],
            'ulasim_durumu': veri['ulasim_durumu'],
            'yasli_nufus_orani': veri['yasli_nufus_orani'],
        }
        tahmin = model_singleton.predict(tahmin_verisi)

        kayit_id = TahminRepository.kaydet(afet_olayi_id, tahmin)

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
            }
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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
