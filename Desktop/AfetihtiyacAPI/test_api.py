import pytest
from api import app, validate_input_data

# Test istemcisi (client) oluşturuyoruz
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# TEST 1 (Görev 1 için): API Endpoint'i doğru veriyle çalışıyor mu?
def test_predict_endpoint_success(client):
    mock_data = {
        "bolge_nufusu": 15000,
        "hasar_durumu": 8
    }
    response = client.post('/predict', json=mock_data)
    
    
    assert response.status_code == 200
    assert response.get_json()['status'] == 'success'


def test_validate_input_missing_data():
    eksik_veri = {"bolge_nufusu": 5000} # hasar_durumu eksik
    is_valid, message = validate_input_data(eksik_veri)
    
    # Doğrulama başarısız olmalı (False) ve hata mesajı dönmeli
    assert is_valid is False
    assert "Eksik parametre" in message


def test_predict_endpoint_bad_request(client):
    response = client.post('/predict', json={"rastgele_veri": 123})
    
    assert response.status_code == 400
    assert response.get_json()['status'] == 'error'