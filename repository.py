from models import db, Bolge, AfetOlayi, TahminKaydi


class BolgeRepository:
    @staticmethod
    def kaydet(ad, il, nufus, ilce=None, lat=None, lon=None):
        bolge = Bolge(ad=ad, il=il, ilce=ilce, nufus=nufus,
                      koordinat_lat=lat, koordinat_lon=lon)
        db.session.add(bolge)
        db.session.commit()
        return bolge.id

    @staticmethod
    def hepsini_getir():
        return Bolge.query.all()

    @staticmethod
    def id_ile_getir(bolge_id):
        return db.session.get(Bolge, bolge_id)

    @staticmethod
    def il_ile_getir(il):
        """Belirli bir ile ait tüm bölgeleri getirir."""
        return Bolge.query.filter_by(il=il).all()

    @staticmethod
    def afet_olaylariyla_getir(bolge_id):
        """Bölgeyi ilişkili afet olaylarıyla birlikte getirir."""
        return Bolge.query.filter_by(id=bolge_id).first()


class AfetOlayiRepository:
    @staticmethod
    def kaydet(bolge_id, veri):
        olay = AfetOlayi(
            bolge_id=bolge_id,
            deprem_buyuklugu=veri['deprem_buyuklugu'],
            bina_yikim_orani=veri['bina_yikim_orani'],
            hava_sicakligi=veri['hava_sicakligi'],
            ulasim_durumu=veri['ulasim_durumu'],
            yasli_nufus_orani=veri['yasli_nufus_orani'],
        )
        db.session.add(olay)
        db.session.commit()
        return olay.id

    @staticmethod
    def id_ile_getir(olay_id):
        return db.session.get(AfetOlayi, olay_id)

    @staticmethod
    def bolgeye_gore_getir(bolge_id):
        """Belirli bir bölgenin tüm afet olaylarını tarihe göre sıralar."""
        return (AfetOlayi.query
                .filter_by(bolge_id=bolge_id)
                .order_by(AfetOlayi.olay_tarihi.desc())
                .all())

    @staticmethod
    def buyukluge_gore_getir(min_buyukluk):
        """Belirtilen büyüklüğün üzerindeki tüm afet olaylarını getirir."""
        return (AfetOlayi.query
                .filter(AfetOlayi.deprem_buyuklugu >= min_buyukluk)
                .order_by(AfetOlayi.deprem_buyuklugu.desc())
                .all())

    @staticmethod
    def tahminlerle_getir(olay_id):
        """Afet olayını ilişkili tahmin kayıtlarıyla birlikte getirir."""
        return (AfetOlayi.query
                .filter_by(id=olay_id)
                .first())


class TahminRepository:
    @staticmethod
    def kaydet(afet_olayi_id, tahmin_sonuclari):
        kayit = TahminKaydi(
            afet_olayi_id=afet_olayi_id,
            acil_barinma=int(tahmin_sonuclari[0]),
            gida=int(tahmin_sonuclari[1]),
            su=int(tahmin_sonuclari[2]),
            medikal=int(tahmin_sonuclari[3]),
            ekip=int(tahmin_sonuclari[4]),
        )
        db.session.add(kayit)
        db.session.commit()
        return kayit.id

    @staticmethod
    def olay_id_ile_getir(afet_olayi_id):
        """Bir afet olayına ait tüm tahmin kayıtlarını getirir."""
        return TahminKaydi.query.filter_by(afet_olayi_id=afet_olayi_id).all()

    @staticmethod
    def bolge_tahminlerini_getir(bolge_id):
        """Bir bölgeye ait tüm tahminleri afet olayıyla join ederek getirir."""
        return (TahminKaydi.query
                .join(AfetOlayi, TahminKaydi.afet_olayi_id == AfetOlayi.id)
                .filter(AfetOlayi.bolge_id == bolge_id)
                .order_by(TahminKaydi.kayit_tarihi.desc())
                .all())

    @staticmethod
    def son_tahmin_getir(afet_olayi_id):
        """Bir afet olayına ait en son tahmin kaydını getirir."""
        return (TahminKaydi.query
                .filter_by(afet_olayi_id=afet_olayi_id)
                .order_by(TahminKaydi.kayit_tarihi.desc())
                .first())
