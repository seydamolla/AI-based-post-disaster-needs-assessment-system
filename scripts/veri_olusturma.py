import pandas as pd
import numpy as np

# Farklı ve dengeli sonuçlar için seed'i değiştirdik
np.random.seed(123)

veri_sayisi = 2000
print(f"🔄 {veri_sayisi} satırlık dengeli veri seti üretiliyor...")

# =====================================================================
# 1. ÖZELLİKLER (FEATURES)
# =====================================================================
nufus = np.random.randint(10000, 6000000, veri_sayisi)
deprem_buyuklugu = np.random.uniform(4.0, 8.5, veri_sayisi)

# Gerçekçi yıkım: 4.0 -> %0, 5.0 -> %1, 6.0 -> %8, 7.0 -> %27, 8.0 -> %64
bina_yikim_orani = np.clip(((deprem_buyuklugu - 4.0) ** 3) / 100, 0.0, 0.85)

# Rastgelelik (Noise) ekle ki model ezberlemesin (Aynı şiddete farklı yıkımlar olabilsin)
bina_yikim_orani = bina_yikim_orani * np.random.uniform(0.5, 1.5, veri_sayisi)
bina_yikim_orani = np.clip(bina_yikim_orani, 0.0, 1.0)
hava_sicakligi = np.random.uniform(-5, 38, veri_sayisi)
ulasim_durumu = np.random.choice([0, 1, 2], veri_sayisi, p=[0.2, 0.5, 0.3])
yasli_nufus_orani = np.random.uniform(0.08, 0.22, veri_sayisi)

# =====================================================================
# 2. DENGELİ HEDEFLER (TARGETS) - np.abs() ile Hata Giderildi
# =====================================================================

# Barınma (Her çadırda ortalama 6 kişi kalır mantığı)
barinma_temel = (nufus * bina_yikim_orani * 0.15) * (1 + (20 - hava_sicakligi)*0.01)
acil_barinma_ihtiyaci = barinma_temel + np.random.normal(0, np.abs(barinma_temel * 0.10))

# Gıda
gida_temel = (nufus * bina_yikim_orani * 0.3)
gida_ihtiyaci = gida_temel + np.random.normal(0, np.abs(gida_temel * 0.08))

# Su
su_temel = (nufus * bina_yikim_orani * 1.5)
su_ihtiyaci = su_temel + np.random.normal(0, np.abs(su_temel * 0.08))

# Medikal (Yaralı sayısı)
medikal_temel = (nufus * bina_yikim_orani * 0.05) * (1 + yasli_nufus_orani)
medikal_ihtiyac = medikal_temel + np.random.normal(0, np.abs(medikal_temel * 0.12))

# Ekip
ekip_temel = (bina_yikim_orani * 150) + (nufus * bina_yikim_orani / 2000)
ekip_ihtiyaci = ekip_temel + np.random.normal(0, np.abs(ekip_temel * 0.15))

# =====================================================================
# 3. VERİ TEMİZLİĞİ VE FORMATLAMA
# =====================================================================
df = pd.DataFrame({
    'nufus': nufus,
    'deprem_buyuklugu': deprem_buyuklugu,
    'bina_yikim_orani': bina_yikim_orani,
    'hava_sicakligi': hava_sicakligi,
    'ulasim_durumu': ulasim_durumu,
    'yasli_nufus_orani': yasli_nufus_orani,
    'acil_barinma_ihtiyaci': acil_barinma_ihtiyaci,
    'gida_ihtiyaci': gida_ihtiyaci,
    'su_ihtiyaci': su_ihtiyaci,
    'medikal_ihtiyac': medikal_ihtiyac,
    'ekip_ihtiyaci': ekip_ihtiyaci
})

# Hedef sütunlarda negatif değerleri sıfırla ve tam sayıya (integer) çevir
hedef_sutunlar = ['acil_barinma_ihtiyaci', 'gida_ihtiyaci', 'su_ihtiyaci', 'medikal_ihtiyac', 'ekip_ihtiyaci']
for kolon in hedef_sutunlar:
    df[kolon] = df[kolon].apply(lambda x: max(0, x)).astype(int)

# =====================================================================
# 4. KAYDETME
# =====================================================================
dosya_adi = "data/dengeli_afet_verisi.csv"
df.to_csv(dosya_adi, index=False)
print(f"✅ İşlem tamam! Yeni ve dengeli veri seti '{dosya_adi}' olarak kaydedildi.")
