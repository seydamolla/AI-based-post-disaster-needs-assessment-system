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
        return Bolge.query.get(bolge_id)


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
        return AfetOlayi.query.get(olay_id)


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
        return TahminKaydi.query.filter_by(afet_olayi_id=afet_olayi_id).all()
