"""
Deploy sirasinda otomatik veritabani kurulumu ve baslangic verisi yukleme.
Render build asamasinda calisir:
  1. Tablolari olusturur (flask db upgrade)
  2. Veritabani bos ise simulasyon verilerini otomatik yukler
"""
import random
from api import app
from models import db, Bolge
from repository import BolgeRepository, AfetOlayiRepository, TahminRepository
from model_singleton import AIModelSingleton

# Gercek Turkiye deprem bolgeleri
BOLGELER = [
    {"ad": "Hatay Merkez", "il": "Hatay", "ilce": "Antakya",
     "nufus": 400000, "lat": 36.20, "lon": 36.16},
    {"ad": "Kahramanmaras Merkez", "il": "Kahramanmaras", "ilce": "Oniksub",
     "nufus": 350000, "lat": 37.58, "lon": 36.93},
    {"ad": "Adiyaman Merkez", "il": "Adiyaman", "ilce": "Merkez",
     "nufus": 250000, "lat": 37.76, "lon": 38.27},
    {"ad": "Gaziantep Merkez", "il": "Gaziantep", "ilce": "Sahinbey",
     "nufus": 1200000, "lat": 37.07, "lon": 37.38},
    {"ad": "Malatya Merkez", "il": "Malatya", "ilce": "Battalgazi",
     "nufus": 450000, "lat": 38.35, "lon": 38.31},
    {"ad": "Diyarbakir Merkez", "il": "Diyarbakir", "ilce": "Baglar",
     "nufus": 600000, "lat": 37.91, "lon": 40.21},
    {"ad": "Osmaniye Merkez", "il": "Osmaniye", "ilce": "Merkez",
     "nufus": 220000, "lat": 37.07, "lon": 36.25},
    {"ad": "Elazig Merkez", "il": "Elazig", "ilce": "Merkez",
     "nufus": 350000, "lat": 38.67, "lon": 39.22},
    {"ad": "Kilis Merkez", "il": "Kilis", "ilce": "Merkez",
     "nufus": 95000, "lat": 36.72, "lon": 37.12},
    {"ad": "Adana Merkez", "il": "Adana", "ilce": "Seyhan",
     "nufus": 900000, "lat": 37.00, "lon": 35.32},
]

# Simulasyon deprem senaryolari (CSV verilerinden turetilmis)
SENARYOLAR = [
    {"deprem_buyuklugu": 7.8, "bina_yikim_orani": 0.784,
     "hava_sicakligi": 5.2, "ulasim_durumu": 0, "yasli_nufus_orani": 0.219},
    {"deprem_buyuklugu": 6.5, "bina_yikim_orani": 0.393,
     "hava_sicakligi": 17.5, "ulasim_durumu": 1, "yasli_nufus_orani": 0.092},
    {"deprem_buyuklugu": 5.9, "bina_yikim_orani": 0.531,
     "hava_sicakligi": -2.2, "ulasim_durumu": 0, "yasli_nufus_orani": 0.137},
    {"deprem_buyuklugu": 7.2, "bina_yikim_orani": 0.829,
     "hava_sicakligi": 31.4, "ulasim_durumu": 2, "yasli_nufus_orani": 0.105},
    {"deprem_buyuklugu": 6.1, "bina_yikim_orani": 0.331,
     "hava_sicakligi": 25.9, "ulasim_durumu": 2, "yasli_nufus_orani": 0.217},
]


def seed_database():
    """Veritabani bos ise baslangic verilerini yukler."""
    with app.app_context():
        # Tablolari olustur (migration yoksa fallback)
        db.create_all()

        # Veritabaninda zaten veri var mi kontrol et
        mevcut_bolge = Bolge.query.count()
        if mevcut_bolge > 0:
            print(f"[SEED] Veritabaninda {mevcut_bolge} bolge mevcut, "
                  "seed atlanıyor.")
            return

        print("[SEED] Veritabani bos, baslangic verileri yukleniyor...")

        # 1. Bolgeleri ekle
        bolge_idler = []
        for bolge in BOLGELER:
            bolge_id = BolgeRepository.kaydet(
                ad=bolge["ad"], il=bolge["il"], nufus=bolge["nufus"],
                ilce=bolge["ilce"], lat=bolge["lat"], lon=bolge["lon"]
            )
            bolge_idler.append(bolge_id)
            print(f"  [+] Bolge: {bolge['ad']} ({bolge['il']}) -> ID: {bolge_id}")

        # 2. Her bolge icin tahmin olustur
        model = AIModelSingleton()
        tahmin_sayisi = 0

        for bolge_id in bolge_idler:
            bolge = BolgeRepository.id_ile_getir(bolge_id)
            # Her bolge icin 2 rastgele senaryo
            secilen = random.sample(SENARYOLAR, min(2, len(SENARYOLAR)))

            for senaryo in secilen:
                # Afet olayi kaydet
                afet_olayi_id = AfetOlayiRepository.kaydet(bolge_id, senaryo)

                # AI tahmini yap
                tahmin_verisi = {
                    "nufus": bolge.nufus,
                    "bina_yikim_orani": senaryo["bina_yikim_orani"],
                    "hava_sicakligi": senaryo["hava_sicakligi"],
                    "ulasim_durumu": senaryo["ulasim_durumu"],
                    "yasli_nufus_orani": senaryo["yasli_nufus_orani"],
                }
                tahmin = model.predict(tahmin_verisi)
                TahminRepository.kaydet(afet_olayi_id, tahmin)
                tahmin_sayisi += 1

        print(f"[SEED] Tamamlandi: {len(bolge_idler)} bolge, "
              f"{tahmin_sayisi} tahmin yuklendi.")


if __name__ == "__main__":
    seed_database()
