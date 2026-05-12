import joblib
import pandas as pd
from flask import Flask, request, jsonify
from models import db
from repository import TahminRepository

app = Flask(__name__)

# Veritabanı Ayarları (Şimdilik lokal bir dosya, CI/CD'de buluta alacağız)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///afet_verileri.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Uygulama ayağa kalkarken tabloları otomatik oluştur
with app.app_context():
    db.create_all()

# Modeli Yükle
try:
    model = joblib.load('afet_ihtiyac_modeli.pkl')
except Exception as e:
    print(f"Model yüklenemedi: {e}")
    model = None

@app.route('/predict', methods=['POST'])
def predict():
    try:
        veri = request.get_json()
        
        # Basit Validasyon (İş Kuralları)
        gerekli_alanlar = ['nufus', 'bina_yikim_orani', 'hava_sicakligi', 'ulasim_durumu', 'yasli_nufus_orani']
        for alan in gerekli_alanlar:
            if alan not in veri:
                return jsonify({'status': 'error', 'message': f'Eksik parametre: {alan}'}), 400

        # Model Tahmini
        df_istek = pd.DataFrame([veri])
        tahmin = model.predict(df_istek)[0]

        # Şov kısmı: Repository üzerinden veritabanına kaydet
        kayit_id = TahminRepository.kaydet(veri, tahmin)

        return jsonify({
            'status': 'success',
            'kayit_id': kayit_id,
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)