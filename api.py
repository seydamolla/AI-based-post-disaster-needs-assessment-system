from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db
from repository import TahminRepository
from model_singleton import AIModelSingleton

app = Flask(__name__)

# Veritabanı Ayarları (Şimdilik lokal bir dosya)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///afet_verileri.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Flask-Migrate entegrasyonu
migrate = Migrate(app, db)

# Yapay zeka modelini Singleton sinifi ile tek sefer yukle
model_singleton = AIModelSingleton()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        veri = request.get_json()
        
        # Basit Validasyon (İş Kuralları)
        gerekli_alanlar = ['nufus', 'bina_yikim_orani', 'hava_sicakligi', 'ulasim_durumu', 'yasli_nufus_orani']
        for alan in gerekli_alanlar:
            if alan not in veri:
                return jsonify({'status': 'error', 'message': f'Eksik parametre: {alan}'}), 400

        # Singleton üzerinden doğrudan tahmin al
        # (DataFrame dönüşümü ve model çağrısı Singleton içinde kapsüllendi)
        tahmin = model_singleton.predict(veri)

        # Repository üzerinden veritabanına kaydet
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
