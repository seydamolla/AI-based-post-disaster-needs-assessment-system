import pandas as pd
import numpy as np

# =====================================================================
# 1. YEREL DOSYADAN HAM VERİYİ OKUMA
# =====================================================================
dosya_yolu = "data/dengeli_afet_verisi.csv"

try:
    df = pd.read_csv(dosya_yolu)
    print(f"📥 '{dosya_yolu}' başarıyla okundu. Toplam satır: {df.shape[0]}")
except FileNotFoundError:
    print(f"❌ Hata: '{dosya_yolu}' bulunamadı. Lütfen önce ham veriyi üreten kodu çalıştırdığınızdan emin olun.")
    # Dosya yoksa kodu durdurmak için boş bir dataframe oluşturuyoruz
    df = pd.DataFrame()

if not df.empty:
    # =====================================================================
    # 2. VERİ TEMİZLEME (DATA CLEANING) AŞAMASI
    # =====================================================================
    print("🧹 Veri temizleme işlemi başlatılıyor...")

    # Adım 1: Çift (Duplicate) Kayıtları Temizleme
    df = df.drop_duplicates()

    # Adım 2: Mantıksız / Aykırı Değerleri (Outliers) Düzeltme
    # Negatif nüfusları ve 60 dereceden yüksek sıcaklıkları siliyoruz (NaN yapıyoruz)
    df.loc[df['nufus'] < 0, 'nufus'] = np.nan
    df.loc[df['hava_sicakligi'] > 60, 'hava_sicakligi'] = np.nan

    # Adım 3: Eksik Verileri (Missing Values / NaN) Doldurma
    # Nüfus için medyan (ortanca), sıcaklık için ortalama kullanıyoruz
    df['nufus'] = df['nufus'].fillna(df['nufus'].median())
    df['hava_sicakligi'] = df['hava_sicakligi'].fillna(df['hava_sicakligi'].mean())

    # Adım 4: Mantıksal Temizlik ve Veri Tipi Dönüşümü
    hedef_sutunlar = ['acil_barinma_ihtiyaci', 'gida_ihtiyaci', 'su_ihtiyaci', 'medikal_ihtiyac', 'ekip_ihtiyaci']

    for kolon in hedef_sutunlar:
        # Negatif ihtiyaç olamaz, max() ile 0'a eşitliyoruz. Küsürat olamaz, int yapıyoruz.
        df[kolon] = df[kolon].apply(lambda x: max(0, x)).astype(int)

    # Nüfusu da tam sayıya çeviriyoruz
    df['nufus'] = df['nufus'].astype(int)

    print(f"✅ Temizlik tamamlandı! Model için hazır temiz veri satır sayısı: {df.shape[0]}")

    # =====================================================================
    # 3. TEMİZLENMİŞ VERİYİ YENİ DOSYA OLARAK KAYDETME
    # =====================================================================
    temiz_dosya = "temiz_afet_verisi.csv"
    df.to_csv(temiz_dosya, index=False)
    print(f"💾 Temizlenmiş veri '{temiz_dosya}' olarak kaydedildi.\n")

    # =====================================================================
    # 4. MODEL İÇİN BÖLÜMLEME (X ve y)
    # =====================================================================
    # Temizlenmiş veriyi direkt RandomForestRegressor modelinize bağlamak için:
    y = df[hedef_sutunlar]
    X = df.drop(hedef_sutunlar, axis=1)
