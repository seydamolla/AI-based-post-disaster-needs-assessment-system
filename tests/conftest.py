"""
Pytest konfigurasyon dosyası.
Bu dosya proje kökünde bulunarak pytest'in modülleri doğru şekilde
bulmasını sağlar ve ortak fixture'ları barındırır.
"""
import pytest
from api import app as flask_app
from models import db as _db


@pytest.fixture(scope='session')
def app():
    """Uygulama fabrikası: test oturumu boyunca tek bir Flask app döner."""
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })
    yield flask_app


@pytest.fixture(scope='function')
def database(app):
    """Her test fonksiyonu için temiz bir veritabanı oluşturur ve sonra temizler."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app, database):
    """Flask test client'ı döner. database fixture'ı otomatik çağrılır."""
    with app.test_client() as test_client:
        yield test_client
