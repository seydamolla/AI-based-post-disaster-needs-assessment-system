import pytest
from models import db as _db, Bolge, AfetOlayi, TahminKaydi
from repository import BolgeRepository, AfetOlayiRepository, TahminRepository
from api import app as flask_app


# ---------- Fixtures ----------

@pytest.fixture(scope='function')
def app():
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })
    yield flask_app


@pytest.fixture(scope='function')
def database(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def ornek_bolge(database, app):
    with app.app_context():
        bolge_id = BolgeRepository.kaydet(
            ad='Kadikoy', il='Istanbul', nufus=500000,
            ilce='Kadikoy', lat=40.99, lon=29.02
        )
        yield bolge_id


@pytest.fixture
def ornek_afet_olayi(ornek_bolge, database, app):
    with app.app_context():
        veri = {
            'deprem_buyuklugu': 6.5,
            'bina_yikim_orani': 0.35,
            'hava_sicakligi': 12.0,
            'ulasim_durumu': 1,
            'yasli_nufus_orani': 0.18,
        }
        olay_id = AfetOlayiRepository.kaydet(ornek_bolge, veri)
        yield olay_id, ornek_bolge


@pytest.fixture
def ornek_tahmin(ornek_afet_olayi, database, app):
    with app.app_context():
        olay_id, bolge_id = ornek_afet_olayi
        tahmin_id = TahminRepository.kaydet(olay_id, [1000, 2500, 15000, 300, 45])
        yield tahmin_id, olay_id, bolge_id


# ============================================================
# BolgeRepository CRUD Testleri
# ============================================================

class TestBolgeRepository:

    def test_bolge_kaydet(self, database, app):
        with app.app_context():
            bolge_id = BolgeRepository.kaydet('Besiktas', 'Istanbul', 200000)
            assert bolge_id is not None
            assert isinstance(bolge_id, int)

    def test_bolge_id_ile_getir(self, ornek_bolge, database, app):
        with app.app_context():
            bolge = BolgeRepository.id_ile_getir(ornek_bolge)
            assert bolge is not None
            assert bolge.ad == 'Kadikoy'
            assert bolge.il == 'Istanbul'
            assert bolge.nufus == 500000

    def test_olmayan_bolge_none_doner(self, database, app):
        with app.app_context():
            bolge = BolgeRepository.id_ile_getir(9999)
            assert bolge is None

    def test_hepsini_getir(self, database, app):
        with app.app_context():
            BolgeRepository.kaydet('Besiktas', 'Istanbul', 200000)
            BolgeRepository.kaydet('Konak', 'Izmir', 300000)
            bolgeler = BolgeRepository.hepsini_getir()
            assert len(bolgeler) == 2

    def test_il_ile_getir(self, database, app):
        with app.app_context():
            BolgeRepository.kaydet('Besiktas', 'Istanbul', 200000)
            BolgeRepository.kaydet('Kadikoy', 'Istanbul', 500000)
            BolgeRepository.kaydet('Konak', 'Izmir', 300000)
            istanbul_bolgeleri = BolgeRepository.il_ile_getir('Istanbul')
            assert len(istanbul_bolgeleri) == 2
            for b in istanbul_bolgeleri:
                assert b.il == 'Istanbul'

    def test_koordinat_kaydedilir(self, database, app):
        with app.app_context():
            bolge_id = BolgeRepository.kaydet(
                'Merkez', 'Ankara', 1000000, lat=39.92, lon=32.85
            )
            bolge = BolgeRepository.id_ile_getir(bolge_id)
            assert bolge.koordinat_lat == 39.92
            assert bolge.koordinat_lon == 32.85


# ============================================================
# AfetOlayiRepository CRUD Testleri
# ============================================================

class TestAfetOlayiRepository:

    def test_afet_olayi_kaydet(self, ornek_bolge, database, app):
        with app.app_context():
            veri = {
                'deprem_buyuklugu': 5.8,
                'bina_yikim_orani': 0.20,
                'hava_sicakligi': 18.0,
                'ulasim_durumu': 2,
                'yasli_nufus_orani': 0.12,
            }
            olay_id = AfetOlayiRepository.kaydet(ornek_bolge, veri)
            assert olay_id is not None

    def test_afet_olayi_id_ile_getir(self, ornek_afet_olayi, database, app):
        with app.app_context():
            olay_id, bolge_id = ornek_afet_olayi
            olay = AfetOlayiRepository.id_ile_getir(olay_id)
            assert olay is not None
            assert olay.deprem_buyuklugu == 6.5
            assert olay.bolge_id == bolge_id

    def test_bolgeye_gore_getir(self, ornek_bolge, database, app):
        with app.app_context():
            for buyukluk in [5.0, 6.0, 7.0]:
                AfetOlayiRepository.kaydet(ornek_bolge, {
                    'deprem_buyuklugu': buyukluk,
                    'bina_yikim_orani': 0.3,
                    'hava_sicakligi': 15.0,
                    'ulasim_durumu': 1,
                    'yasli_nufus_orani': 0.15,
                })
            olaylar = AfetOlayiRepository.bolgeye_gore_getir(ornek_bolge)
            assert len(olaylar) == 3
            for o in olaylar:
                assert o.bolge_id == ornek_bolge

    def test_buyukluge_gore_getir(self, ornek_bolge, database, app):
        with app.app_context():
            for buyukluk in [4.5, 6.2, 7.8]:
                AfetOlayiRepository.kaydet(ornek_bolge, {
                    'deprem_buyuklugu': buyukluk,
                    'bina_yikim_orani': 0.3,
                    'hava_sicakligi': 15.0,
                    'ulasim_durumu': 1,
                    'yasli_nufus_orani': 0.15,
                })
            buyuk_olaylar = AfetOlayiRepository.buyukluge_gore_getir(6.0)
            assert len(buyuk_olaylar) == 2
            for o in buyuk_olaylar:
                assert o.deprem_buyuklugu >= 6.0


# ============================================================
# TahminRepository CRUD Testleri
# ============================================================

class TestTahminRepository:

    def test_tahmin_kaydet(self, ornek_afet_olayi, database, app):
        with app.app_context():
            olay_id, _ = ornek_afet_olayi
            tahmin_id = TahminRepository.kaydet(olay_id, [800, 2000, 12000, 250, 40])
            assert tahmin_id is not None

    def test_tahmin_degerler_dogru_kaydedilir(self, ornek_afet_olayi, database, app):
        with app.app_context():
            olay_id, _ = ornek_afet_olayi
            tahmin_id = TahminRepository.kaydet(olay_id, [1000, 2500, 15000, 300, 45])
            tahmin = _db.session.get(TahminKaydi, tahmin_id)
            assert tahmin.acil_barinma == 1000
            assert tahmin.gida == 2500
            assert tahmin.su == 15000
            assert tahmin.medikal == 300
            assert tahmin.ekip == 45

    def test_olay_id_ile_getir(self, ornek_afet_olayi, database, app):
        with app.app_context():
            olay_id, _ = ornek_afet_olayi
            TahminRepository.kaydet(olay_id, [800, 2000, 12000, 250, 40])
            TahminRepository.kaydet(olay_id, [900, 2100, 13000, 260, 42])
            tahminler = TahminRepository.olay_id_ile_getir(olay_id)
            assert len(tahminler) == 2

    def test_son_tahmin_getir(self, ornek_afet_olayi, database, app):
        with app.app_context():
            olay_id, _ = ornek_afet_olayi
            TahminRepository.kaydet(olay_id, [800, 2000, 12000, 250, 40])
            TahminRepository.kaydet(olay_id, [999, 3000, 20000, 400, 60])
            son = TahminRepository.son_tahmin_getir(olay_id)
            assert son is not None
            assert son.acil_barinma == 999

    def test_bolge_tahminlerini_getir(self, ornek_tahmin, database, app):
        with app.app_context():
            _, olay_id, bolge_id = ornek_tahmin
            tahminler = TahminRepository.bolge_tahminlerini_getir(bolge_id)
            assert len(tahminler) >= 1
            for t in tahminler:
                assert t.afet_olayi_id == olay_id


# ============================================================
# İlişki Testleri
# ============================================================

class TestIliskiler:

    def test_bolge_afet_olayi_iliskisi(self, ornek_afet_olayi, database, app):
        with app.app_context():
            olay_id, bolge_id = ornek_afet_olayi
            bolge = BolgeRepository.afet_olaylariyla_getir(bolge_id)
            assert bolge is not None
            assert len(bolge.afet_olaylari) == 1
            assert bolge.afet_olaylari[0].id == olay_id

    def test_afet_olayi_tahmin_iliskisi(self, ornek_tahmin, database, app):
        with app.app_context():
            tahmin_id, olay_id, _ = ornek_tahmin
            olay = AfetOlayiRepository.tahminlerle_getir(olay_id)
            assert olay is not None
            assert len(olay.tahmin_kayitlari) == 1
            assert olay.tahmin_kayitlari[0].id == tahmin_id

    def test_uclu_iliski_zinciri(self, ornek_tahmin, database, app):
        """Bolge -> AfetOlayi -> TahminKaydi zinciri dogru kurulmus olmali."""
        with app.app_context():
            tahmin_id, olay_id, bolge_id = ornek_tahmin
            bolge = BolgeRepository.afet_olaylariyla_getir(bolge_id)
            assert len(bolge.afet_olaylari) == 1
            olay = bolge.afet_olaylari[0]
            assert len(olay.tahmin_kayitlari) == 1
            assert olay.tahmin_kayitlari[0].id == tahmin_id

    def test_farkli_bolgelerin_tahminleri_karismiyor(self, database, app):
        with app.app_context():
            bolge1_id = BolgeRepository.kaydet('Kadikoy', 'Istanbul', 500000)
            bolge2_id = BolgeRepository.kaydet('Konak', 'Izmir', 300000)
            veri = {
                'deprem_buyuklugu': 5.5, 'bina_yikim_orani': 0.2,
                'hava_sicakligi': 20.0, 'ulasim_durumu': 1, 'yasli_nufus_orani': 0.1
            }
            olay1_id = AfetOlayiRepository.kaydet(bolge1_id, veri)
            olay2_id = AfetOlayiRepository.kaydet(bolge2_id, veri)
            TahminRepository.kaydet(olay1_id, [100, 200, 500, 50, 10])
            TahminRepository.kaydet(olay2_id, [200, 400, 1000, 100, 20])

            tahminler1 = TahminRepository.bolge_tahminlerini_getir(bolge1_id)
            tahminler2 = TahminRepository.bolge_tahminlerini_getir(bolge2_id)
            assert len(tahminler1) == 1
            assert len(tahminler2) == 1
            assert tahminler1[0].afet_olayi_id != tahminler2[0].afet_olayi_id
