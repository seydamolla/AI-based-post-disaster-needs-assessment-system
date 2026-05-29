# AI Tabanlı Afet Sonrası İhtiyaç Ölçeklendirmesi

Deprem sonrası bölgeye göre acil ihtiyaçları (barınma, gıda, su, medikal, ekip) tahmin eden AI destekli API.

## 🌐 Canlı URL
**https://afet-bf7c.onrender.com**

## 📡 API Endpointleri
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/bolge` | Yeni bölge ekle |
| GET | `/bolge` | Tüm bölgeleri listele |
| POST | `/predict` | Deprem tahmini yap |
| GET | `/tahminler/<id>` | Tahmin sonuçlarını getir |

## 🗄️ Veritabanı
- **Bulut:** Supabase PostgreSQL (eu-central-1)
- **ORM:** Flask-SQLAlchemy

## ⚙️ CI/CD Pipeline
- **Platform:** GitHub Actions
- **Test:** Her PR'da otomatik testler çalışır
- **Deploy:** main'e merge sonrası Render'a otomatik deploy

## 🛠️ Kurulum (Lokal)
```bash
pip install -r requirements.txt
flask --app api.py db upgrade
python api.py
```
