# AI Tabanli Afet Sonrasi Ihtiyac Olceklendirmesi

Deprem sonrasi bolgeye gore acil ihtiyaclari (barinma, gida, su, medikal, ekip) tahmin eden AI destekli API.

## Canli URL
**https://afet-bf7c.onrender.com/bolge**

## API Endpointleri
| Method | Endpoint | Aciklama |
|--------|----------|----------|
| POST | `/bolge` | Yeni bolge ekle |
| GET | `/bolge` | Tum bolgeleri listele |
| POST | `/predict` | Deprem tahmini yap |
| GET | `/tahminler/<id>` | Tahmin sonuclarini getir |

## Veritabani
- **Bulut:** Supabase PostgreSQL (eu-central-1)
- **ORM:** Flask-SQLAlchemy
- **Migration:** Flask-Migrate (Alembic)
- **Seed:** Deploy sirasinda otomatik (`seed.py`)

## CI/CD Pipeline (GitHub Actions)

PR acildiginda ve main branch'e push yapildiginda otomatik olarak calisir:

```
PR Acildi / Push
    |
    v
[1. BUILD & LINT]  ->  flake8 ile kod kalitesi kontrolu
    |                   + import dogrulama (build check)
    v
[2. TEST]          ->  pytest ile tum testler calisir
    |                   (singleton, repository, API)
    v
[3. DEPLOY]        ->  Sadece main branch'te calisir
    |                   Render'a otomatik deploy tetiklenir
    v
[Render Build]     ->  pip install + flask db upgrade + python seed.py
    |
    v
[CANLI]            ->  https://afet-bf7c.onrender.com
```

### Pipeline Asamalari
| Asama | Icerik | Tetiklenme |
|-------|--------|------------|
| Build & Lint | flake8 + import kontrolu | Her PR ve push |
| Test | pytest (singleton, repository, API) | Her PR ve push |
| Deploy | Render deploy hook tetikleme | Sadece main merge |

## Ortam Degiskenleri ve Secret Yonetimi

Hassas bilgiler **asla kod icerisinde tutulmaz**:

| Degisken | Nerede Yonetiliyor | Aciklama |
|----------|-------------------|----------|
| `DATABASE_URL` | Render Dashboard + GitHub Secrets | Supabase PostgreSQL baglanti bilgisi |
| `RENDER_DEPLOY_HOOK_URL` | GitHub Secrets | Otomatik deploy tetikleme URL'si |
| `PYTHON_VERSION` | render.yaml | Hassas degil, acik tutulabilir |

- **Lokal gelistirme:** `.env` dosyasi kullanilir (`.gitignore` ile korunur)
- **Bulut ortami:** Render Environment Variables
- **CI/CD:** GitHub Repository Secrets

## Kurulum (Lokal)
```bash
# 1. Bagimliliklari yukle
pip install -r requirements.txt

# 2. Ortam degiskenlerini ayarla
cp .env.example .env

# 3. Veritabani migration
flask --app api.py db upgrade

# 4. Baslangic verisi yukle (opsiyonel)
python seed.py

# 5. Uygulamayi baslat
python api.py
```

## Proje Yapisi
```
├── .github/workflows/ci.yml   # CI/CD pipeline (build, lint, test, deploy)
├── api.py                      # Flask API endpointleri
├── models.py                   # SQLAlchemy veritabani modelleri
├── repository.py               # Repository pattern (CRUD islemleri)
├── model_singleton.py          # AI model Singleton deseni
├── seed.py                     # Otomatik veritabani seed scripti
├── render.yaml                 # Render deploy konfigurasyonu
├── requirements.txt            # Python bagimliliklari
├── .env.example                # Ortam degiskenleri sablonu
├── .gitignore                  # Git ignore kurallari
├── test_api.py                 # API unit testleri
├── test_repository.py          # Repository unit testleri
└── test_model_singleton.py     # Singleton unit testleri
```
