import pytest
import numpy as np
from model_singleton import AIModelSingleton


# ---------- Yardımcı Sahte Model ----------

class FakeModel:
    def predict(self, df):
        return np.array([[10, 20, 30, 40, 50]])


# ---------- Fixture ----------

@pytest.fixture(autouse=True)
def singleton_sifirla():
    """Her testten önce ve sonra Singleton state'ini sıfırlar."""
    original_instance = AIModelSingleton._instance
    original_model = AIModelSingleton._model
    AIModelSingleton._instance = None
    AIModelSingleton._model = None
    yield
    AIModelSingleton._instance = original_instance
    AIModelSingleton._model = original_model


@pytest.fixture
def fake_singleton(monkeypatch):
    """Gerçek .pkl dosyasına ihtiyaç duymadan FakeModel yükleyen Singleton döner."""
    monkeypatch.setattr("model_singleton.joblib.load", lambda _: FakeModel())
    return AIModelSingleton("dummy.pkl")


# ============================================================
# Singleton Tasarım Deseni Testleri
# ============================================================

class TestSingletonDeseni:

    def test_ayni_instance_doner(self, monkeypatch):
        monkeypatch.setattr("model_singleton.joblib.load", lambda _: FakeModel())
        birinci = AIModelSingleton("dummy.pkl")
        ikinci = AIModelSingleton("dummy.pkl")
        assert birinci is ikinci

    def test_model_sadece_bir_kez_yuklenir(self, monkeypatch):
        yukleme_sayisi = {"adet": 0}

        def sayici_yukle(_path):
            yukleme_sayisi["adet"] += 1
            return FakeModel()

        monkeypatch.setattr("model_singleton.joblib.load", sayici_yukle)

        AIModelSingleton("dummy.pkl")
        AIModelSingleton("dummy.pkl")
        AIModelSingleton("dummy.pkl")

        assert yukleme_sayisi["adet"] == 1

    def test_get_model_modeli_doner(self, fake_singleton):
        assert fake_singleton.get_model() is not None
        assert isinstance(fake_singleton.get_model(), FakeModel)


# ============================================================
# Model Yükleme Testleri
# ============================================================

class TestModelYukleme:

    def test_model_basariyla_yuklenir(self, monkeypatch):
        monkeypatch.setattr("model_singleton.joblib.load", lambda _: FakeModel())
        singleton = AIModelSingleton("dummy.pkl")
        assert singleton.get_model() is not None

    def test_model_dosyasi_bulunamazsa_none_olur(self, monkeypatch):
        def yukleyemez(_path):
            raise FileNotFoundError("dosya yok")
        monkeypatch.setattr("model_singleton.joblib.load", yukleyemez)
        singleton = AIModelSingleton("olmayan.pkl")
        assert singleton.get_model() is None

    def test_model_bozuk_dosyada_none_olur(self, monkeypatch):
        def bozuk_yukle(_path):
            raise Exception("dosya bozuk")
        monkeypatch.setattr("model_singleton.joblib.load", bozuk_yukle)
        singleton = AIModelSingleton("bozuk.pkl")
        assert singleton.get_model() is None


# ============================================================
# Predict Metodu Testleri
# ============================================================

class TestPredict:

    def test_predict_dogru_sonuc_doner(self, fake_singleton):
        veri = {
            'nufus': 50000,
            'bina_yikim_orani': 0.4,
            'hava_sicakligi': 15.0,
            'ulasim_durumu': 1,
            'yasli_nufus_orani': 0.15,
        }
        sonuc = fake_singleton.predict(veri)
        assert list(sonuc) == [10, 20, 30, 40, 50]

    def test_predict_model_yoksa_exception_firlatir(self, monkeypatch):
        def yukleyemez(_path):
            raise FileNotFoundError("dosya yok")
        monkeypatch.setattr("model_singleton.joblib.load", yukleyemez)
        singleton = AIModelSingleton("olmayan.pkl")
        with pytest.raises(Exception, match="tahmin yapılamıyor"):
            singleton.predict({'nufus': 100, 'ulasim_durumu': 0})

    def test_predict_ulasim_one_hot_encoding_ulasim0(self, monkeypatch):
        """ulasim_durumu=0 → ulasim_durumu_1=0, ulasim_durumu_2=0 olmalı."""
        yakalanan = {}

        class KontrolModel:
            def predict(self, df):
                yakalanan['df'] = df
                return np.array([[1, 2, 3, 4, 5]])

        monkeypatch.setattr("model_singleton.joblib.load", lambda _: KontrolModel())
        singleton = AIModelSingleton("dummy.pkl")
        singleton.predict({'nufus': 100, 'bina_yikim_orani': 0.3,
                           'hava_sicakligi': 20.0, 'ulasim_durumu': 0,
                           'yasli_nufus_orani': 0.1})

        df = yakalanan['df']
        assert 'ulasim_durumu' not in df.columns
        assert df.iloc[0]['ulasim_durumu_1'] == 0
        assert df.iloc[0]['ulasim_durumu_2'] == 0

    def test_predict_ulasim_one_hot_encoding_ulasim1(self, monkeypatch):
        """ulasim_durumu=1 → ulasim_durumu_1=1, ulasim_durumu_2=0 olmalı."""
        yakalanan = {}

        class KontrolModel:
            def predict(self, df):
                yakalanan['df'] = df
                return np.array([[1, 2, 3, 4, 5]])

        monkeypatch.setattr("model_singleton.joblib.load", lambda _: KontrolModel())
        singleton = AIModelSingleton("dummy.pkl")
        singleton.predict({'nufus': 100, 'bina_yikim_orani': 0.3,
                           'hava_sicakligi': 20.0, 'ulasim_durumu': 1,
                           'yasli_nufus_orani': 0.1})

        df = yakalanan['df']
        assert df.iloc[0]['ulasim_durumu_1'] == 1
        assert df.iloc[0]['ulasim_durumu_2'] == 0

    def test_predict_ulasim_one_hot_encoding_ulasim2(self, monkeypatch):
        """ulasim_durumu=2 → ulasim_durumu_1=0, ulasim_durumu_2=1 olmalı."""
        yakalanan = {}

        class KontrolModel:
            def predict(self, df):
                yakalanan['df'] = df
                return np.array([[1, 2, 3, 4, 5]])

        monkeypatch.setattr("model_singleton.joblib.load", lambda _: KontrolModel())
        singleton = AIModelSingleton("dummy.pkl")
        singleton.predict({'nufus': 100, 'bina_yikim_orani': 0.3,
                           'hava_sicakligi': 20.0, 'ulasim_durumu': 2,
                           'yasli_nufus_orani': 0.1})

        df = yakalanan['df']
        assert df.iloc[0]['ulasim_durumu_1'] == 0
        assert df.iloc[0]['ulasim_durumu_2'] == 1

    def test_predict_orijinal_veri_degistirilmez(self, fake_singleton):
        """predict() orijinal veri sözlüğünü değiştirmemeli."""
        veri = {
            'nufus': 50000,
            'bina_yikim_orani': 0.4,
            'hava_sicakligi': 15.0,
            'ulasim_durumu': 1,
            'yasli_nufus_orani': 0.15,
        }
        orijinal_anahtarlar = set(veri.keys())
        fake_singleton.predict(veri)
        assert set(veri.keys()) == orijinal_anahtarlar

    def test_predict_bes_deger_doner(self, fake_singleton):
        veri = {
            'nufus': 30000, 'bina_yikim_orani': 0.5,
            'hava_sicakligi': 10.0, 'ulasim_durumu': 0, 'yasli_nufus_orani': 0.2
        }
        sonuc = fake_singleton.predict(veri)
        assert len(sonuc) == 5
