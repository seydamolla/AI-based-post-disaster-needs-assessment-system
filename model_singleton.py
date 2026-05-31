import joblib
import pandas as pd


class AIModelSingleton:
    """
    Singleton Tasarım Deseni ile ML modelini yöneten sınıf.
    Uygulama yaşam döngüsü boyunca sadece tek bir örneği (instance) oluşturulur.
    ~20MB'lık model dosyası bellekte bir kez tutulur, tüm istekler aynı referansı kullanır.
    """
    _instance = None
    _model = None

    def __new__(cls, model_path='data/afet_ihtiyac_modeli.pkl'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._model = cls._load_model(model_path)
        return cls._instance

    @classmethod
    def _load_model(cls, model_path):
        """Modeli diskten sadece bir kere belleğe (RAM) yükler."""
        try:
            model = joblib.load(model_path)
            print("Makine öğrenmesi modeli başarıyla yüklendi (Singleton).")
            return model
        except Exception as exc:
            print(f"Model yuklenemedi: {exc}")
            return None

    def get_model(self):
        """Geriye uyumluluk için raw model erişimi."""
        return self._model

    def predict(self, veri_sozlugu):
        """
        Dışarıdan gelen veri sözlüğünü kullanarak tahmin döndürür.
        Eğitim sırasında yapılan ön işleme (one-hot encoding) burada da uygulanır.
        Böylece API katmanının veri dönüşümü ile ilgilenmesine gerek kalmaz.
        """
        if self._model is None:
            raise Exception("Model yüklenmediği için tahmin yapılamıyor.")

        # Eğitim scriptindeki ön işleme adımını uygula:
        # ulasim_durumu (0, 1, 2) → one-hot encoding (drop_first=True)
        # Sonuç: ulasim_durumu_1 ve ulasim_durumu_2 dummy sütunları
        veri = dict(veri_sozlugu)
        ulasim = veri.pop('ulasim_durumu')
        veri['ulasim_durumu_1'] = 1 if str(ulasim) == '1' else 0
        veri['ulasim_durumu_2'] = 1 if str(ulasim) == '2' else 0

        df_istek = pd.DataFrame([veri])
        return self._model.predict(df_istek)[0]
