import pytest
from api import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    from models import db
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_predict_endpoint_success(client):
    mock_data = {
        "nufus": 50000,
        "bina_yikim_orani": 0.45,
        "hava_sicakligi": -2.5,
        "ulasim_durumu": 0,
        "yasli_nufus_orani": 0.15
    }
    response = client.post('/predict', json=mock_data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert 'kayit_id' in json_data
    assert 'sonuclar' in json_data

def test_predict_endpoint_missing_data(client):
    eksik_veri = {
        "nufus": 50000,
        "bina_yikim_orani": 0.45,
        "ulasim_durumu": 0,
        "yasli_nufus_orani": 0.15
    }
    response = client.post('/predict', json=eksik_veri)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'

def test_predict_endpoint_bad_request(client):
    response = client.post('/predict', json={"rastgele_veri": 123})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
