import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Eğer kodları farklı hücrelerde çalıştırıyorsanız ve df hafızadan silindiyse,
# aşağıdaki satırın başındaki '#' işaretini kaldırarak temiz dosyayı okutabilirsiniz:
# df = pd.read_csv("temiz_afet_verisi.csv")

print("🚀 Model hazırlıkları başlıyor...\n")

# Ulaşım durumu sayısal (0,1,2) olduğu için modelin bunu bir 'kategori' olarak algılaması adına string'e çeviriyoruz.
# Böylece pd.get_dummies fonksiyonu bunu 3 farklı durum olarak (açık, kapalı, kısmen) düzgünce kodlayacaktır.
df['ulasim_durumu'] = df['ulasim_durumu'].astype(str)

# --- 1. HEDEF VE ÖZELLİK (X, y) AYRIMI ---
hedef_sutunlar = ['acil_barinma_ihtiyaci', 'gida_ihtiyaci', 'su_ihtiyaci', 'medikal_ihtiyac', 'ekip_ihtiyaci']
y = df[hedef_sutunlar]
X = df.drop(hedef_sutunlar, axis=1)

# Kategorik verileri (One-Hot Encoding) dönüştürme
X = pd.get_dummies(X, drop_first=True)

# --- 2. EĞİTİM VE TEST VERİSİ OLARAK BÖLME ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- 3. VERİ ÖLÇEKLENDİRME (Standardizasyon) ---
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# --- 4. MODEL EĞİTİMİ ---
print("Sayısal tahmin modeli (RandomForestRegressor) eğitiliyor, lütfen bekleyin...")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# ⚠️ Sizin kodunuzdaki eksik kısım eklendi: Modelin test verisi üzerinde tahmin yapması (y_pred oluşturulması)
y_pred = model.predict(X_test_scaled)

# Canlı sisteme (Web veya Mobil) entegre etmek için modeli ve scaler'ı kaydediyoruz
joblib.dump(model, 'afet_ihtiyac_modeli.pkl')
joblib.dump(scaler, 'afet_scaler.pkl')
print("💾 Model ('afet_ihtiyac_modeli.pkl') ve Scaler ('afet_scaler.pkl') başarıyla kaydedildi!\n")

# --- 5. SONUÇLARI DEĞERLENDİRME VE RAPORLAMA ---
print("✅ Eğitim Tamamlandı! İşte Sayısal Tahmin Hata Raporları:\n")

for i, kolon_adi in enumerate(hedef_sutunlar):
    gercek_degerler = y_test[kolon_adi]
    tahmin_edilenler = y_pred[:, i]

    mae = mean_absolute_error(gercek_degerler, tahmin_edilenler)
    r2 = r2_score(gercek_degerler, tahmin_edilenler)

    ortalama_ihtiyac = np.mean(gercek_degerler)
    if ortalama_ihtiyac > 0:
        hata_yuzdesi = (mae / ortalama_ihtiyac) * 100
        basari_yuzdesi = 100 - hata_yuzdesi
    else:
        hata_yuzdesi = 0
        basari_yuzdesi = 100

    print(f"{'-'*40}")
    print(f"🎯 {kolon_adi.upper()} Tahmin Başarısı:")
    print(f"{'-'*40}")
    print(f"Ortalama Hata Payı (MAE) : ± {mae:.2f} birim")
    print(f"Modelin Sapma Yüzdesi    : % {hata_yuzdesi:.2f}")
    print(f"Modelin Başarı Yüzdesi   : % {basari_yuzdesi:.2f} (Tahmini)")
    print(f"R-Kare Skoru (R2)        : {r2:.2f}")
    print("\n")
