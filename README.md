# AI Tabanlı Afet Sonrası İhtiyaç Ölçeklendirmesi

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Flask](https://img.shields.io/badge/Flask-API-green)
![Gemini](https://img.shields.io/badge/Gemini-AI-purple)

Deprem sonrası bölgeye göre acil ihtiyaçları (barınma, gıda, su, medikal, ekip) makine öğrenmesi algoritmalarıyla tahmin eden ve **Gemini API** ile kapsamlı değerlendirme raporları üreten AI destekli projedir. Projede hem güçlü bir Backend API hem de etkileşimli bir Frontend arayüzü bulunmaktadır.

## 🚀 Canlı Sistem URL
**https://afet-bf7c.onrender.com/bolge**

---

## ✨ Özellikler (Features)

- **Makine Öğrenmesi Destekli Tahminler:** Geçmiş verilere dayalı karar ağaçları/regresyon algoritmalarıyla en yakın tahmini ihtiyaçların çıkarılması.
- **Yapay Zeka (LLM) Analiz Raporları:** Üretilen rakamların Gemini API kullanılarak doğal dilde lojistik planlarına ve kısa değerlendirmelere dönüştürülmesi.
- **Etkileşimli Frontend (Web Arayüzü):** Kullanıcıların afet bölgelerini ve verileri anlık olarak girip sonuçları görebileceği entegre bir web sayfası.
- **Otomatik CI/CD:** Her push ve PR'da kodun test edilip (pytest) otomatik canlı ortama (Render) aktarılması.

---

## 🛠 Kullanılan Teknolojiler (Tech Stack)

### Backend
- **Dil:** Python 3.x
- **Framework:** Flask
- **Veritabanı:** Supabase PostgreSQL (eu-central-1)
- **ORM & Migration:** Flask-SQLAlchemy, Flask-Migrate (Alembic)
- **Yapay Zeka:** Gemini AI (Google GenAI)

### Frontend
- **Diller:** HTML5, CSS3, JavaScript (Vanilla JS)

---

## 📂 Proje Yapısı

```text
AfetihtiyacAPI_new/
├── .github/workflows/   # CI/CD pipeline (build, lint, test, deploy)
├── api.py               # Ana Flask API endpointleri
├── app.py               # WSGI giriş noktası (Render için)
├── models.py            # SQLAlchemy veritabanı modelleri
├── repository.py        # Repository pattern (CRUD işlemleri)
├── model_singleton.py   # AI model Singleton deseni
├── gemini_service.py    # Google Gemini entegrasyonu ve servis katmanı
├── seed.py              # Otomatik veritabanı seed scripti
├── render.yaml          # Render deploy konfigürasyonu
├── requirements.txt     # Python bağımlılıkları
├── .env.example         # Ortam değişkenleri şablonu
├── data/                # Makine Öğrenmesi Modeli ve Veri Setleri
│   ├── afet_ihtiyac_modeli.pkl
│   └── dengeli_afet_verisi.csv
├── frontend/            # Web Arayüzü Kodları
│   ├── index.html
│   ├── style.css
│   └── app.js
└── tests/               # Pytest Unit Testleri
    ├── conftest.py
    └── test_*.py
```

---

## 🌐 API Endpointleri

### Temel CRUD ve Tahmin
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/bolge` | Yeni bölge ekle |
| GET | `/bolge` | Tüm bölgeleri listele |
| POST | `/predict` | Deprem tahmini yap ve kaydet |
| GET | `/tahminler/<id>` | Tahmin sonuçlarını getir |

### Yapay Zeka (Gemini AI)
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/ai/analiz` | Tahminlere dayalı detaylı rapor |
| POST | `/ai/ozetle` | Bölgenin tüm tahminlerinin özeti |
| POST | `/ai/oneri` | Lojistik ve kaynak dağıtım önerileri |

### Bölge ve Tahmin İsteklerinde Veri Kontrolü

`POST /bolge` ve `POST /predict`, `Content-Type: application/json` ile bir JSON
nesnesi bekler. Bozuk JSON, liste/null gövde, eksik alan veya geçersiz değer
gönderildiğinde `400` ve `{"status": "error", "message": "..."}` döner.
Doğrulama, veritabanı işlemlerinden ve model çağrısından önce yapılır.

- `nufus`: 0–2147483647 arasında tam sayı; `bolge_id`: 1–2147483647 arasında tam sayı.
- `bina_yikim_orani` ve `yasli_nufus_orani`: 0–1 arasında sayı (yüzde değil oran).
- `ulasim_durumu`: 0, 1 veya 2 tam sayılarından biri.
- `deprem_buyuklugu`: negatif olmayan sonlu sayı; `hava_sicakligi`: sonlu sayı.
- `ad`/`il`: boş olmayan, sırasıyla en fazla 100/50 karakterlik metin.
  İsteğe bağlı `ilce`, null veya boş olmayan en fazla 50 karakterlik metindir.
- İsteğe bağlı koordinatlar null olabilir; enlem −90–90, boylam −180–180 aralığındadır.
- Sayısal alanlarda metin (`"50000"`), boolean (`true`/`false`), NaN ve sonsuzluk kabul edilmez.

Bu kontroller veri biçimini doğrular; modelin tahmin doğruluğunu veya gerçek afet
koşullarına uygunluğunu doğrulamaz.

---

## 💻 Kurulum ve Çalıştırma (Lokal)

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin.

### 1. Backend Kurulumu
```bash
# 1. Bağımlılıkları yükle
pip install -r requirements.txt

# 2. Ortam değişkenlerini ayarla
# .env.example dosyasının ismini .env olarak değiştirip GEMINI_API_KEY ve DATABASE_URL girin.
cp .env.example .env

# 3. Veritabanı migration ve seed işlemi
flask --app api.py db upgrade
python seed.py

# 4. Sunucuyu başlat
python api.py
```

### 2. Frontend'in Çalıştırılması
Backend sunucusu arka planda çalışırken (`localhost:5000`), `frontend` klasörü içindeki `index.html` dosyasına çift tıklayarak tarayıcınızda açmanız yeterlidir. Arayüz otomatik olarak lokal sunucunuzla iletişime geçecektir.

---

## ⚙️ Ortam Değişkenleri ve Secret Yönetimi

Hassas bilgiler **asla kod içerisinde tutulmaz**:

| Değişken | Nerede Yönetiliyor | Açıklama |
|----------|-------------------|----------|
| `DATABASE_URL` | Render / GitHub Secrets | Supabase PostgreSQL bağlantı bilgisi |
| `GEMINI_API_KEY` | Render / .env | Gemini AI entegrasyonu API Anahtarı |
| `RENDER_DEPLOY_HOOK_URL`| GitHub Secrets | Otomatik deploy tetikleme URL'si |

---

## 🤝 Katkıda Bulunma (Contributing)

1. Projeyi Fork'layın
2. Yeni bir dal oluşturun (`git checkout -b feature/YeniOzellik`)
3. Değişikliklerinizi commit'leyin (`git commit -m 'feat: Yeni bir özellik eklendi'`)
4. Dalınıza pushlayın (`git push origin feature/YeniOzellik`)
5. Bir Pull Request açın

## 📄 Lisans
Bu proje MIT Lisansı ile lisanslanmıştır.
