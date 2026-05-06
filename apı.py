from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

try:
    model = joblib.load('afet_ihtiyac_modeli.pkl')
except Exception as e:
    model = None

if __name__ == '__main__':
    app.run(debug=True, port=5000)
