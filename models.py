from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TahminKaydi(db.Model):
    __tablename__ = 'tahmin_kayitlari'

    id = db.Column(db.Integer, primary_key=True)
    nufus = db.Column(db.Integer, nullable=False)
    bina_yikim_orani = db.Column(db.Float, nullable=False)
    hava_sicakligi = db.Column(db.Float, nullable=False)
    ulasim_durumu = db.Column(db.Integer, nullable=False)
    yasli_nufus_orani = db.Column(db.Float, nullable=False)
    
    barinma_sonucu = db.Column(db.Integer, nullable=False)
    gida_sonucu = db.Column(db.Integer, nullable=False)
    su_sonucu = db.Column(db.Integer, nullable=False)
    medikal_sonucu = db.Column(db.Integer, nullable=False)
    ekip_sonucu = db.Column(db.Integer, nullable=False)
    
    kayit_tarihi = db.Column(db.DateTime, default=datetime.utcnow)