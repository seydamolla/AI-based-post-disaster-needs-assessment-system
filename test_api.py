import pytest
from flask_migrate import Migrate


# ---------- API Endpoint Testleri ----------

def test_predict_endpoint_success(client):
    """Geçerli veri ile tahmin endpoint'inin başarılı yanıt döndüğünü doğrular."""
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
    """Eksik parametre gönderildiğinde 400 hatası döndüğünü doğrular."""
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
    """Tamamen geçersiz veri gönderildiğinde 400 döndüğünü doğrular."""
    response = client.post('/predict', json={"rastgele_veri": 123})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'


# ---------- Flask-Migrate Entegrasyon Testleri ----------

def test_migrate_extension_registered(app):
    """Flask-Migrate'in uygulama üzerinde doğru şekilde kayıtlı olduğunu doğrular."""
    assert 'migrate' in app.extensions, "Flask-Migrate app.extensions içinde kayıtlı olmalı"


def test_migrate_instance_type(app):
    """Migrate nesnesinin doğru tipte olduğunu doğrular."""
    migrate_ext = app.extensions['migrate']
    assert migrate_ext is not None
    assert migrate_ext.db is not None


def test_database_tables_created(app, database):
    """Migration sonrası veritabanı tablolarının oluştuğunu doğrular."""
    from sqlalchemy import inspect
    with app.app_context():
        inspector = inspect(database.engine)
        tables = inspector.get_table_names()
        assert 'tahmin_kayitlari' in tables, "tahmin_kayitlari tablosu oluşturulmuş olmalı"


def test_database_columns_match_model(app, database):
    """Veritabanı sütunlarının model tanımıyla eşleştiğini doğrular."""
    from sqlalchemy import inspect
    expected_columns = [
        'id', 'nufus', 'bina_yikim_orani', 'hava_sicakligi',
        'ulasim_durumu', 'yasli_nufus_orani', 'barinma_sonucu',
        'gida_sonucu', 'su_sonucu', 'medikal_sonucu',
        'ekip_sonucu', 'kayit_tarihi'
    ]
    with app.app_context():
        inspector = inspect(database.engine)
        columns = [col['name'] for col in inspector.get_columns('tahmin_kayitlari')]
        for col_name in expected_columns:
            assert col_name in columns, f"'{col_name}' sütunu tabloda bulunmalı"
