from models import db, TahminKaydi

class TahminRepository:
    @staticmethod
    def kaydet(veri_sozlugu, tahmin_sonuclari):
        yeni_kayit = TahminKaydi(
            nufus=veri_sozlugu['nufus'],
            bina_yikim_orani=veri_sozlugu['bina_yikim_orani'],
            hava_sicakligi=veri_sozlugu['hava_sicakligi'],
            ulasim_durumu=veri_sozlugu['ulasim_durumu'],
            yasli_nufus_orani=veri_sozlugu['yasli_nufus_orani'],
            barinma_sonucu=int(tahmin_sonuclari[0]),
            gida_sonucu=int(tahmin_sonuclari[1]),
            su_sonucu=int(tahmin_sonuclari[2]),
            medikal_sonucu=int(tahmin_sonuclari[3]),
            ekip_sonucu=int(tahmin_sonuclari[4])
        )
        db.session.add(yeni_kayit)
        db.session.commit()
        return yeni_kayit.id