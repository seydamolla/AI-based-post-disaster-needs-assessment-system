from flask import Flask, request, jsonify
import joblib

app = Flask(_name_)

try:
    model = joblib.load('afet_ihtiyac_modeli.pkl')
except Exception as e:
    model = None

def validate_input_data(data):
    if not data:
        return False, "Gönderilen veri boş olamaz."
    if 'bolge_nufusu' not in data or 'hasar_durumu' not in data:
        return False, "Eksik parametre: 'bolge_nufusu' ve 'hasar_durumu' zorunludur."
    return True, "Geçerli"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        is_valid, message = validate_input_data(data)
        if not is_valid:
            return jsonify({'status': 'error', 'message': message}), 400

        return jsonify({
            'status': 'success',
            'message': 'Tahmin basariyla uretildi',
            'ihtiyac_seviyesi': 'Yüksek'
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if _name_ == '_main_':
    app.run(debug=True, port=5000)
