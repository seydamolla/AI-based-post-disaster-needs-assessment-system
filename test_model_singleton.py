from model_singleton import AIModelSingleton


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
