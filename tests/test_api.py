import pytest
from unittest.mock import Mock


# ---------- Yardımcı Fonksiyon ----------

def _bolge_olustur(client):
    """Test için bir bölge oluşturur ve id'sini döner."""
    bolge_data = {
        "ad": "Test Bölgesi",
        "il": "Ankara",
        "ilce": "Çankaya",
        "nufus": 50000,
        "koordinat_lat": 39.9334,
        "koordinat_lon": 32.8597
    }
    response = client.post('/bolge', json=bolge_data)
    return response


# ---------- Bölge Endpoint Testleri ----------

def test_bolge_ekle_success(client):
    """Geçerli veri ile bölge eklemenin başarılı olduğunu doğrular."""
    response = _bolge_olustur(client)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert 'bolge_id' in json_data


def test_bolge_ekle_missing_data(client):
    """Eksik parametre ile bölge eklemenin 400 döndüğünü doğrular."""
    response = client.post('/bolge', json={"ad": "Test"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'


def test_bolgeleri_listele(client):
    """Bölge listesinin döndüğünü doğrular."""
    _bolge_olustur(client)
    response = client.get('/bolge')
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) >= 1
    assert json_data[0]['ad'] == 'Test Bölgesi'


# ---------- Predict Endpoint Testleri ----------

def test_predict_endpoint_success(client, monkeypatch):
    """Geçerli veri ile tahmin endpoint'inin başarılı yanıt döndüğünü doğrular."""
    # Gerçek API çağrısı yapmamak için gemini_service mocklanır
    import api
    class MockGemini:
        def kisa_degerlendirme_olustur(self, bolge, tahmin):
            return "Test yapay zeka özeti."
    monkeypatch.setattr(api, "gemini_service", MockGemini())

    # Önce bir bölge oluştur
    bolge_resp = _bolge_olustur(client)
    bolge_id = bolge_resp.get_json()['bolge_id']

    mock_data = {
        "bolge_id": bolge_id,
        "deprem_buyuklugu": 6.5,
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
    assert 'afet_olayi_id' in json_data
    assert 'sonuclar' in json_data
    assert 'bolge' in json_data
    assert 'ai_ozet' in json_data
    assert json_data['ai_ozet'] == "Test yapay zeka özeti."


def test_predict_endpoint_missing_data(client):
    """Eksik parametre gönderildiğinde 400 hatası döndüğünü doğrular."""
    eksik_veri = {
        "bolge_id": 1,
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


def test_predict_endpoint_invalid_bolge(client):
    """Var olmayan bölge id ile 404 döndüğünü doğrular."""
    mock_data = {
        "bolge_id": 9999,
        "deprem_buyuklugu": 5.0,
        "bina_yikim_orani": 0.3,
        "hava_sicakligi": 10.0,
        "ulasim_durumu": 1,
        "yasli_nufus_orani": 0.1
    }
    response = client.post('/predict', json=mock_data)
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data['status'] == 'error'


def test_predict_endpoint_exception(client, monkeypatch):
    """Sistemde beklenmeyen bir hata (Exception) oluştuğunda 500 döndüğünü doğrular."""
    # Veritabanında bir hata simüle etmek için repository'yi mockluyoruz
    def fake_id_ile_getir(bolge_id):
        raise Exception("Beklenmeyen veritabanı hatası")

    monkeypatch.setattr("api.BolgeRepository.id_ile_getir", fake_id_ile_getir)

    mock_data = {
        "bolge_id": 1,
        "deprem_buyuklugu": 5.0,
        "bina_yikim_orani": 0.3,
        "hava_sicakligi": 10.0,
        "ulasim_durumu": 1,
        "yasli_nufus_orani": 0.1
    }
    response = client.post('/predict', json=mock_data)
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert 'Beklenmeyen' in json_data['message']
# ---------- Tahminler Endpoint Testleri ----------

def test_tahminleri_getir(client):
    """Tahmin sonuçlarının afet olayı id ile getirilebildiğini doğrular."""
    bolge_resp = _bolge_olustur(client)
    bolge_id = bolge_resp.get_json()['bolge_id']

    predict_data = {
        "bolge_id": bolge_id,
        "deprem_buyuklugu": 7.0,
        "bina_yikim_orani": 0.6,
        "hava_sicakligi": 5.0,
        "ulasim_durumu": 2,
        "yasli_nufus_orani": 0.2
    }
    predict_resp = client.post('/predict', json=predict_data)
    afet_olayi_id = predict_resp.get_json()['afet_olayi_id']

    response = client.get(f'/tahminler/{afet_olayi_id}')
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) >= 1


def test_tahminleri_getir_not_found(client):
    """Var olmayan afet olayı id ile 404 döndüğünü doğrular."""
    response = client.get('/tahminler/9999')
    assert response.status_code == 404


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
    """Migration sonrası tüm veritabanı tablolarının oluştuğunu doğrular."""
    from sqlalchemy import inspect
    with app.app_context():
        inspector = inspect(database.engine)
        tables = inspector.get_table_names()
        assert 'bolgeler' in tables, "bolgeler tablosu oluşturulmuş olmalı"
        assert 'afet_olaylari' in tables, "afet_olaylari tablosu oluşturulmuş olmalı"
        assert 'tahmin_kayitlari' in tables, "tahmin_kayitlari tablosu oluşturulmuş olmalı"


def test_database_columns_bolge(app, database):
    """Bölge tablosu sütunlarının model tanımıyla eşleştiğini doğrular."""
    from sqlalchemy import inspect
    expected = ['id', 'ad', 'il', 'ilce', 'nufus', 'koordinat_lat', 'koordinat_lon']
    with app.app_context():
        inspector = inspect(database.engine)
        columns = [col['name'] for col in inspector.get_columns('bolgeler')]
        for col_name in expected:
            assert col_name in columns, f"'{col_name}' sütunu bolgeler tablosunda bulunmalı"


def test_database_columns_afet_olayi(app, database):
    """AfetOlayi tablosu sütunlarının model tanımıyla eşleştiğini doğrular."""
    from sqlalchemy import inspect
    expected = ['id', 'bolge_id', 'deprem_buyuklugu', 'bina_yikim_orani',
                'hava_sicakligi', 'ulasim_durumu', 'yasli_nufus_orani', 'olay_tarihi']
    with app.app_context():
        inspector = inspect(database.engine)
        columns = [col['name'] for col in inspector.get_columns('afet_olaylari')]
        for col_name in expected:
            assert col_name in columns, f"'{col_name}' sütunu afet_olaylari tablosunda bulunmalı"


def test_database_columns_tahmin_kaydi(app, database):
    """TahminKaydi tablosu sütunlarının model tanımıyla eşleştiğini doğrular."""
    from sqlalchemy import inspect
    expected = ['id', 'afet_olayi_id', 'acil_barinma', 'gida', 'su',
                'medikal', 'ekip', 'kayit_tarihi']
    with app.app_context():
        inspector = inspect(database.engine)
        columns = [col['name'] for col in inspector.get_columns('tahmin_kayitlari')]
        for col_name in expected:
            assert col_name in columns, f"'{col_name}' sütunu tahmin_kayitlari tablosunda bulunmalı"


# ---------- İstek Doğrulama Regresyon Testleri ----------

@pytest.fixture
def prediction_spy(monkeypatch):
    import api
    model = Mock(return_value=[10, 20, 30, 40, 50])
    monkeypatch.setattr(api.model_singleton, 'predict', model)
    monkeypatch.setattr(api, 'gemini_service', None)
    return model


def _gecerli_tahmin(bolge_id):
    return {
        'bolge_id': bolge_id, 'deprem_buyuklugu': 6.5,
        'bina_yikim_orani': 0.4, 'hava_sicakligi': -5,
        'ulasim_durumu': 1, 'yasli_nufus_orani': 0.2,
    }


def _tahmin_kaydi_yok(app):
    from models import AfetOlayi, TahminKaydi
    with app.app_context():
        assert AfetOlayi.query.count() == 0
        assert TahminKaydi.query.count() == 0


@pytest.mark.parametrize('endpoint', ['/bolge', '/predict'])
@pytest.mark.parametrize('body,content_type', [
    ('null', 'application/json'), ('[]', 'application/json'),
    ('["ad", "il", "nufus"]', 'application/json'),
    ('"metin"', 'application/json'), ('42', 'application/json'),
    ('true', 'application/json'), ('{', 'application/json'),
    ('', 'application/json'), ('{}', 'text/plain'), ('{}', None),
])
def test_invalid_request_body(client, app, prediction_spy, endpoint, body, content_type):
    from models import Bolge
    response = client.post(endpoint, data=body, content_type=content_type)
    assert response.status_code == 400
    assert response.get_json()['status'] == 'error'
    assert response.get_json()['message']
    prediction_spy.assert_not_called()
    with app.app_context():
        assert Bolge.query.count() == 0
    _tahmin_kaydi_yok(app)


@pytest.mark.parametrize('field,value', [
    ('nufus', -1), ('nufus', '50000'), ('nufus', 1.5),
    ('nufus', True), ('nufus', None), ('nufus', 2147483648),
    ('nufus', float('nan')), ('nufus', float('inf')),
    ('ad', ''), ('ad', '   '), ('ad', None), ('ad', 123),
    ('ad', 'a' * 101), ('il', 'i' * 51), ('il', False),
    ('ilce', []), ('ilce', 'i' * 51),
    ('koordinat_lat', 90.1), ('koordinat_lat', -90.1),
    ('koordinat_lon', 180.1), ('koordinat_lon', -180.1),
    ('koordinat_lat', float('nan')), ('koordinat_lon', '30'),
])
def test_invalid_region_does_not_write(client, app, field, value):
    from models import Bolge
    payload = {'ad': 'Test', 'il': 'Ankara', 'nufus': 50000, field: value}
    response = client.post('/bolge', json=payload)
    assert response.status_code == 400
    assert field in response.get_json()['message']
    with app.app_context():
        assert Bolge.query.count() == 0


@pytest.mark.parametrize('field,value', [
    ('bolge_id', 0), ('bolge_id', -1), ('bolge_id', '1'),
    ('bolge_id', True), ('bolge_id', 1.0), ('bolge_id', 2147483648),
    ('deprem_buyuklugu', -1), ('deprem_buyuklugu', '6.5'),
    ('deprem_buyuklugu', float('inf')), ('deprem_buyuklugu', 10 ** 400),
    ('bina_yikim_orani', -0.1), ('bina_yikim_orani', 1.1),
    ('bina_yikim_orani', True), ('bina_yikim_orani', None),
    ('bina_yikim_orani', float('nan')),
    ('yasli_nufus_orani', -0.1), ('yasli_nufus_orani', 1.1),
    ('yasli_nufus_orani', '0.2'), ('yasli_nufus_orani', float('-inf')),
    ('ulasim_durumu', -1), ('ulasim_durumu', 3),
    ('ulasim_durumu', 1.5), ('ulasim_durumu', False),
    ('ulasim_durumu', '1'), ('ulasim_durumu', 1.0),
    ('hava_sicakligi', None), ('hava_sicakligi', '20'),
    ('hava_sicakligi', float('nan')), ('hava_sicakligi', float('inf')),
])
def test_invalid_prediction_has_no_side_effects(client, app, prediction_spy, field, value):
    bolge_id = _bolge_olustur(client).get_json()['bolge_id']
    payload = _gecerli_tahmin(bolge_id)
    payload[field] = value
    response = client.post('/predict', json=payload)
    assert response.status_code == 400
    assert field in response.get_json()['message']
    prediction_spy.assert_not_called()
    _tahmin_kaydi_yok(app)


@pytest.mark.parametrize('nufus,lat,lon', [(0, -90, -180), (2147483647, 90, 180)])
def test_region_boundary_values(client, nufus, lat, lon):
    payload = {'ad': 'Test', 'il': 'Ankara', 'nufus': nufus,
               'koordinat_lat': lat, 'koordinat_lon': lon, 'ilce': None}
    assert client.post('/bolge', json=payload).status_code == 201


@pytest.mark.parametrize('yikim,yasli,ulasim', [(0, 0, 0), (1, 1, 2), (0.5, 0.2, 1)])
def test_prediction_boundary_values(client, app, prediction_spy, yikim, yasli, ulasim):
    from models import AfetOlayi, TahminKaydi
    bolge_id = _bolge_olustur(client).get_json()['bolge_id']
    payload = _gecerli_tahmin(bolge_id)
    payload.update(bina_yikim_orani=yikim, yasli_nufus_orani=yasli, ulasim_durumu=ulasim)
    response = client.post('/predict', json=payload)
    assert response.status_code == 200
    if yikim == 0:
        prediction_spy.assert_not_called()
        assert set(response.get_json()['sonuclar'].values()) == {0}
    else:
        prediction_spy.assert_called_once()
        assert response.get_json()['sonuclar']['gida'] == 20
    with app.app_context():
        assert AfetOlayi.query.count() == 1
        assert TahminKaydi.query.count() == 1
