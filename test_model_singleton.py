import pytest
from model_singleton import AIModelSingleton


@pytest.fixture(autouse=True)
def reset_singleton():
    """Her testten sonra Singleton state'ini geri yükle.
    Böylece bu dosyadaki testler diğer test dosyalarının Singleton'ını bozmaz."""
    original_instance = AIModelSingleton._instance
    original_model = AIModelSingleton._model
    yield
    AIModelSingleton._instance = original_instance
    AIModelSingleton._model = original_model


def test_singleton_returns_same_instance():
    first_instance = AIModelSingleton()
    second_instance = AIModelSingleton()

    assert first_instance is second_instance


def test_singleton_loads_model_once(monkeypatch):
    AIModelSingleton._instance = None
    AIModelSingleton._model = None

    load_call_count = {"count": 0}

    def fake_load(_path):
        load_call_count["count"] += 1
        return "mock_model"

    monkeypatch.setattr("model_singleton.joblib.load", fake_load)

    first_instance = AIModelSingleton("dummy.pkl")
    second_instance = AIModelSingleton("dummy.pkl")

    assert first_instance is second_instance
    assert first_instance.get_model() == "mock_model"
    assert load_call_count["count"] == 1


def test_singleton_predict_delegates_to_model(monkeypatch):
    """predict() metodunun DataFrame dönüşümü yapıp modele doğru delege ettiğini test eder."""
    AIModelSingleton._instance = None
    AIModelSingleton._model = None

    import numpy as np

    class FakeModel:
        def predict(self, df):
            # One-hot encoding sonrası sütunları kontrol et
            assert 'ulasim_durumu' not in df.columns, "ulasim_durumu one-hot encode edilmeli"
            assert 'ulasim_durumu_1' in df.columns
            assert 'ulasim_durumu_2' in df.columns
            assert df.iloc[0]['nufus'] == 100
            # ulasim_durumu=1 → ulasim_durumu_1=1, ulasim_durumu_2=0
            assert df.iloc[0]['ulasim_durumu_1'] == 1
            assert df.iloc[0]['ulasim_durumu_2'] == 0
            return np.array([[10, 20, 30, 40, 50]])

    def fake_load(_path):
        return FakeModel()

    monkeypatch.setattr("model_singleton.joblib.load", fake_load)

    singleton = AIModelSingleton("dummy.pkl")
    sonuc = singleton.predict({'nufus': 100, 'bina_yikim_orani': 0.5, 'ulasim_durumu': 1})

    assert list(sonuc) == [10, 20, 30, 40, 50]


def test_singleton_predict_raises_when_no_model(monkeypatch):
    """Model yüklenmediğinde predict() çağrılırsa Exception fırlatıldığını test eder."""
    AIModelSingleton._instance = None
    AIModelSingleton._model = None

    def fake_load(_path):
        raise FileNotFoundError("dosya yok")

    monkeypatch.setattr("model_singleton.joblib.load", fake_load)

    singleton = AIModelSingleton("nonexistent.pkl")

    import pytest
    with pytest.raises(Exception, match="tahmin yapılamıyor"):
        singleton.predict({'nufus': 100, 'ulasim_durumu': 0})

