from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class Bolge(db.Model):
    __tablename__ = 'bolgeler'

    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    il = db.Column(db.String(50), nullable=False)
    ilce = db.Column(db.String(50), nullable=True)
    nufus = db.Column(db.Integer, nullable=False)
    koordinat_lat = db.Column(db.Float, nullable=True)
    koordinat_lon = db.Column(db.Float, nullable=True)

    afet_olaylari = db.relationship('AfetOlayi', back_populates='bolge', lazy=True)

    def __repr__(self):
        return f'<Bolge {self.ad} - {self.il}>'


class AfetOlayi(db.Model):
    __tablename__ = 'afet_olaylari'

    id = db.Column(db.Integer, primary_key=True)
    bolge_id = db.Column(db.Integer, db.ForeignKey('bolgeler.id'), nullable=False)
    deprem_buyuklugu = db.Column(db.Float, nullable=False)
    bina_yikim_orani = db.Column(db.Float, nullable=False)
    hava_sicakligi = db.Column(db.Float, nullable=False)
    ulasim_durumu = db.Column(db.Integer, nullable=False)    # 0=kapali, 1=kismi, 2=acik
    yasli_nufus_orani = db.Column(db.Float, nullable=False)
    olay_tarihi = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    bolge = db.relationship('Bolge', back_populates='afet_olaylari')
    tahmin_kayitlari = db.relationship('TahminKaydi', back_populates='afet_olayi', lazy=True)

    def __repr__(self):
        return f'<AfetOlayi {self.id} - Buyukluk:{self.deprem_buyuklugu}>'


class TahminKaydi(db.Model):
    __tablename__ = 'tahmin_kayitlari'

    id = db.Column(db.Integer, primary_key=True)
    afet_olayi_id = db.Column(db.Integer, db.ForeignKey('afet_olaylari.id'), nullable=False)

    acil_barinma = db.Column(db.Integer, nullable=False)
    gida = db.Column(db.Integer, nullable=False)
    su = db.Column(db.Integer, nullable=False)
    medikal = db.Column(db.Integer, nullable=False)
    ekip = db.Column(db.Integer, nullable=False)

    kayit_tarihi = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    afet_olayi = db.relationship('AfetOlayi', back_populates='tahmin_kayitlari')

    def __repr__(self):
        return f'<TahminKaydi {self.id} - Olay:{self.afet_olayi_id}>'
