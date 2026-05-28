import joblib


class AIModelSingleton:
    _instance = None
    _model = None

    def __new__(cls, model_path='afet_ihtiyac_modeli.pkl'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._model = cls._load_model(model_path)
        return cls._instance

    @classmethod
    def _load_model(cls, model_path):
        try:
            return joblib.load(model_path)
        except Exception as exc:
            print(f"Model yuklenemedi: {exc}")
            return None

    def get_model(self):
        return self._model
