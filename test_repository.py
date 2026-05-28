import pytest
from models import Bolge, AfetOlayi, TahminKaydi
from repository import BolgeRepository, AfetOlayiRepository, TahminRepository

# ---------- BolgeRepository Testleri ----------

def test_bolge_kaydet(app, database):
    """Bolge kaydetme işlemini test eder."""
    with app.app_context():
        bolge_id = BolgeRepository.kaydet(
            ad="Kadıköy", il="İstanbul", nufus=482000,
            ilce="Kadıköy", lat=40.9818, lon=29.0270
        )
        assert bolge_id is not None
        bolge = database.session.get(Bolge, bolge_id)
        assert bolge is not None
        assert bolge.ad == "Kadıköy"


def test_bolge_hepsini_getir(app, database):
    """Tüm bölgeleri getirme işlemini test eder."""
    with app.app_context():
        BolgeRepository.kaydet(ad="Merkez", il="Bursa", nufus=10000)
        BolgeRepository.kaydet(ad="Merkez", il="Ankara", nufus=20000)
        
        bolgeler = BolgeRepository.hepsini_getir()
        assert len(bolgeler) == 2


def test_bolge_id_ile_getir(app, database):
    """ID ile bölge getirme işlemini test eder."""
    with app.app_context():
        bolge_id = BolgeRepository.kaydet(ad="Merkez", il="İzmir", nufus=30000)
        bolge = BolgeRepository.id_ile_getir(bolge_id)
        assert bolge is not None
        assert bolge.il == "İzmir"


def test_bolge_il_ile_getir(app, database):
    """İl ismine göre bölge getirme işlemini test eder."""
    with app.app_context():
        BolgeRepository.kaydet(ad="Bornova", il="İzmir", nufus=30000)
        BolgeRepository.kaydet(ad="Karşıyaka", il="İzmir", nufus=20000)
        BolgeRepository.kaydet(ad="Merkez", il="Ankara", nufus=50000)
        
        izmir_bolgeleri = BolgeRepository.il_ile_getir("İzmir")
        assert len(izmir_bolgeleri) == 2
        assert all(b.il == "İzmir" for b in izmir_bolgeleri)


def test_bolge_afet_olaylariyla_getir(app, database):
    """Bölge ve ilişkili afet olaylarını getirme işlemini test eder."""
    with app.app_context():
        bolge_id = BolgeRepository.kaydet(ad="Merkez", il="Düzce", nufus=100000)
        AfetOlayiRepository.kaydet(bolge_id, {
            'deprem_buyuklugu': 5.5, 'bina_yikim_orani': 0.1, 
            'hava_sicakligi': 15, 'ulasim_durumu': 2, 'yasli_nufus_orani': 0.1
        })
        
        bolge = BolgeRepository.afet_olaylariyla_getir(bolge_id)
        assert bolge is not None
        assert len(bolge.afet_olaylari) == 1
        assert bolge.afet_olaylari[0].deprem_buyuklugu == 5.5


# ---------- AfetOlayiRepository Testleri ----------

def test_afet_olayi_kaydet(app, database):
    """Afet olayı kaydetme işlemini test eder."""
    with app.app_context():
        bolge_id = BolgeRepository.kaydet(ad="Merkez", il="Van", nufus=100000)
        olay_veri = {
            'deprem_buyuklugu': 7.2, 'bina_yikim_orani': 0.4, 
            'hava_sicakligi': -5, 'ulasim_durumu': 0, 'yasli_nufus_orani': 0.08
        }
        olay_id = AfetOlayiRepository.kaydet(bolge_id, olay_veri)
        
        assert olay_id is not None
        olay = database.session.get(AfetOlayi, olay_id)
        assert olay is not None
        assert olay.deprem_buyuklugu == 7.2
        assert olay.bolge_id == bolge_id


def test_afet_olayi_bolgeye_gore_getir(app, database):
    """Bölgeye göre afet olaylarını getirme işlemini test eder."""
    with app.app_context():
        bolge_id = BolgeRepository.kaydet(ad="Merkez", il="Erzincan", nufus=50000)
        AfetOlayiRepository.kaydet(bolge_id, {
            'deprem_buyuklugu': 4.0, 'bina_yikim_orani': 0.0, 
            'hava_sicakligi': 10, 'ulasim_durumu': 2, 'yasli_nufus_orani': 0.1
        })
        AfetOlayiRepository.kaydet(bolge_id, {
            'deprem_buyuklugu': 6.0, 'bina_yikim_orani': 0.2, 
            'hava_sicakligi': 5, 'ulasim_durumu': 1, 'yasli_nufus_orani': 0.1
        })
        
        olaylar = AfetOlayiRepository.bolgeye_gore_getir(bolge_id)
        assert len(olaylar) == 2
        # order_by(olay_tarihi.desc()) ile en son eklenen en başta olmalı.
        # Bu testte ikisi çok hızlı eklendiği için tarihleri aynı olabilir, ama en azından sayıyı kontrol ediyoruz.


def test_afet_olayi_buyukluge_gore_getir(app, database):
    """Belirtilen büyüklüğün üzerindeki afet olaylarını getirmeyi test eder."""
    with app.app_context():
        bolge_id = BolgeRepository.kaydet(ad="Merkez", il="Manisa", nufus=50000)
        AfetOlayiRepository.kaydet(bolge_id, {
            'deprem_buyuklugu': 3.5, 'bina_yikim_orani': 0.0, 
            'hava_sicakligi': 20, 'ulasim_durumu': 2, 'yasli_nufus_orani': 0.1
        })
        AfetOlayiRepository.kaydet(bolge_id, {
            'deprem_buyuklugu': 5.8, 'bina_yikim_orani': 0.1, 
            'hava_sicakligi': 18, 'ulasim_durumu': 1, 'yasli_nufus_orani': 0.1
        })
        
        buyuk_olaylar = AfetOlayiRepository.buyukluge_gore_getir(5.0)
        assert len(buyuk_olaylar) == 1
        assert buyuk_olaylar[0].deprem_buyuklugu == 5.8


def test_afet_olayi_tahminlerle_getir(app, database):
    """Afet olayı ve ilişkili tahminleri getirmeyi test eder."""
    with app.app_context():
        bolge_id = BolgeRepository.kaydet(ad="Merkez", il="Kocaeli", nufus=1000000)
        olay_id = AfetOlayiRepository.kaydet(bolge_id, {
            'deprem_buyuklugu': 7.4, 'bina_yikim_orani': 0.5, 
            'hava_sicakligi': 25, 'ulasim_durumu': 0, 'yasli_nufus_orani': 0.05
        })
        TahminRepository.kaydet(olay_id, [1000, 2000, 3000, 4000, 500])
        
        olay = AfetOlayiRepository.tahminlerle_getir(olay_id)
        assert olay is not None
        assert len(olay.tahmin_kayitlari) == 1
        assert olay.tahmin_kayitlari[0].acil_barinma == 1000


# ---------- TahminRepository Testleri ----------

def test_tahmin_kaydet(app, database):
    """Tahmin kaydetme işlemini test eder."""
    with app.app_context():
        bolge_id = BolgeRepository.kaydet(ad="Merkez", il="Bolu", nufus=50000)
        olay_id = AfetOlayiRepository.kaydet(bolge_id, {
            'deprem_buyuklugu': 6.0, 'bina_yikim_orani': 0.2, 
            'hava_sicakligi': 5, 'ulasim_durumu': 1, 'yasli_nufus_orani': 0.1
        })
        kayit_id = TahminRepository.kaydet(olay_id, [100, 200, 300, 400, 50])
        
        assert kayit_id is not None
        kayit = database.session.get(TahminKaydi, kayit_id)
        assert kayit is not None
        assert kayit.afet_olayi_id == olay_id
        assert kayit.acil_barinma == 100


def test_tahmin_olay_id_ile_getir(app, database):
    """Bir afet olayına ait tüm tahminleri getirmeyi test eder."""
    with app.app_context():
        bolge_id = BolgeRepository.kaydet(ad="Merkez", il="Antalya", nufus=500000)
        olay_id = AfetOlayiRepository.kaydet(bolge_id, {
            'deprem_buyuklugu': 4.5, 'bina_yikim_orani': 0.0, 
            'hava_sicakligi': 30, 'ulasim_durumu': 2, 'yasli_nufus_orani': 0.15
        })
        TahminRepository.kaydet(olay_id, [10, 20, 30, 40, 5])
        TahminRepository.kaydet(olay_id, [15, 25, 35, 45, 10])
        
        tahminler = TahminRepository.olay_id_ile_getir(olay_id)
        assert len(tahminler) == 2


def test_tahmin_bolge_tahminlerini_getir(app, database):
    """Bir bölgeye ait tüm tahminleri getirmeyi test eder."""
    with app.app_context():
        bolge_id = BolgeRepository.kaydet(ad="Merkez", il="Muğla", nufus=200000)
        olay_id1 = AfetOlayiRepository.kaydet(bolge_id, {
            'deprem_buyuklugu': 5.0, 'bina_yikim_orani': 0.1, 
            'hava_sicakligi': 25, 'ulasim_durumu': 2, 'yasli_nufus_orani': 0.2
        })
        olay_id2 = AfetOlayiRepository.kaydet(bolge_id, {
            'deprem_buyuklugu': 4.0, 'bina_yikim_orani': 0.0, 
            'hava_sicakligi': 25, 'ulasim_durumu': 2, 'yasli_nufus_orani': 0.2
        })
        
        TahminRepository.kaydet(olay_id1, [100, 200, 300, 400, 50])
        TahminRepository.kaydet(olay_id2, [10, 20, 30, 40, 5])
        
        tahminler = TahminRepository.bolge_tahminlerini_getir(bolge_id)
        assert len(tahminler) == 2


def test_tahmin_son_tahmin_getir(app, database):
    """Bir afet olayına ait en son tahmini getirmeyi test eder."""
    with app.app_context():
        bolge_id = BolgeRepository.kaydet(ad="Merkez", il="Burdur", nufus=80000)
        olay_id = AfetOlayiRepository.kaydet(bolge_id, {
            'deprem_buyuklugu': 5.5, 'bina_yikim_orani': 0.1, 
            'hava_sicakligi': 15, 'ulasim_durumu': 2, 'yasli_nufus_orani': 0.1
        })
        import time
        TahminRepository.kaydet(olay_id, [10, 20, 30, 40, 5])
        time.sleep(0.1) # Tarih farkı oluşması için
        TahminRepository.kaydet(olay_id, [100, 200, 300, 400, 50])
        
        son_tahmin = TahminRepository.son_tahmin_getir(olay_id)
        assert son_tahmin is not None
        assert son_tahmin.acil_barinma == 100
