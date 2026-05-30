"""
Gemini API Servis Modülü
========================
Google Gemini API ile iletişimi yöneten servis sınıfı.
Afet sonrası ihtiyaç analizi, özet çıkarma ve lojistik öneri üretme
senaryolarında kullanılır.

Güncel google-genai SDK'sı kullanılmaktadır.
"""

import os
from google import genai


class GeminiService:
    """
    Gemini API ile iletişimi yöneten servis sınıfı.
    Afet sonrası yapay zekâ destekli analiz, özetleme ve öneri üretir.
    """

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY ortam değişkeni bulunamadı.")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = 'gemini-flash-latest'

    def analiz_raporu_olustur(self, bolge, tahmin, afet_verisi):
        """
        Tahmin sonuçlarını ve bölge verilerini kullanarak
        Gemini'den kapsamlı bir afet durum analizi raporu üretir.

        Args:
            bolge: Bölge nesnesi (ad, il, ilce, nufus)
            tahmin: TahminKaydi nesnesi (acil_barinma, gida, su, medikal, ekip)
            afet_verisi: AfetOlayi nesnesi (deprem_buyuklugu, bina_yikim_orani, vb.)

        Returns:
            str: Gemini'nin ürettiği analiz raporu metni
        """
        prompt = f"""Sen bir afet yönetimi uzmanısın. Aşağıdaki verilere dayanarak
kapsamlı bir afet durum analizi raporu oluştur.

## Bölge Bilgileri
- Bölge Adı: {bolge.ad}
- İl: {bolge.il}
- İlçe: {bolge.ilce or 'Belirtilmemiş'}
- Nüfus: {bolge.nufus:,}

## Afet Verileri
- Deprem Büyüklüğü: {afet_verisi.deprem_buyuklugu}
- Bina Yıkım Oranı: %{afet_verisi.bina_yikim_orani * 100:.1f}
- Hava Sıcaklığı: {afet_verisi.hava_sicakligi}°C
- Ulaşım Durumu: {_ulasim_durumu_metin(afet_verisi.ulasim_durumu)}
- Yaşlı Nüfus Oranı: %{afet_verisi.yasli_nufus_orani * 100:.1f}

## ML Modeli Tahmin Sonuçları
- Acil Barınma İhtiyacı: {tahmin.acil_barinma} birim
- Gıda İhtiyacı: {tahmin.gida} birim
- Su İhtiyacı: {tahmin.su} birim
- Medikal İhtiyaç: {tahmin.medikal} birim
- Kurtarma Ekibi İhtiyacı: {tahmin.ekip} ekip

Lütfen aşağıdaki başlıklar altında Türkçe analiz raporu oluştur:
1. **Genel Durum Değerlendirmesi**: Afetin şiddetini ve etkisini sınıflandır (Düşük/Orta/Yüksek/Kritik)
2. **Risk Analizi**: Bölgenin özel risk faktörlerini analiz et
3. **İhtiyaç Önceliklendirmesi**: Tahmin sonuçlarına göre hangi ihtiyacın önce karşılanması gerektiğini sırala ve gerekçelendir
4. **Kritik Uyarılar**: Dikkat edilmesi gereken özel durumlar (yaşlı nüfus, hava koşulları, ulaşım)
5. **Acil Eylem Önerileri**: İlk 24-48 saat için yapılması gerekenler
"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text

    def tahminleri_ozetle(self, bolge, tahmin_listesi):
        """
        Bir bölgedeki birden fazla afet olayının tahmin sonuçlarını
        Gemini ile özetleyerek karşılaştırmalı analiz yapar.

        Args:
            bolge: Bölge nesnesi
            tahmin_listesi: TahminKaydi nesnelerinin listesi (ilişkili afet_olayi ile)

        Returns:
            str: Gemini'nin ürettiği karşılaştırmalı özet metni
        """
        tahmin_satirlari = ""
        for i, tahmin in enumerate(tahmin_listesi, 1):
            olay = tahmin.afet_olayi
            tahmin_satirlari += f"""
### Olay #{i} (Tarih: {tahmin.kayit_tarihi.strftime('%d.%m.%Y %H:%M')})
- Deprem Büyüklüğü: {olay.deprem_buyuklugu}
- Acil Barınma: {tahmin.acil_barinma} | Gıda: {tahmin.gida} | Su: {tahmin.su}
- Medikal: {tahmin.medikal} | Ekip: {tahmin.ekip}
"""

        prompt = f"""Sen bir afet yönetimi veri analistisin. Aşağıdaki bölgeye ait
birden fazla afet olayının tahmin sonuçlarını analiz edip özet rapor oluştur.

## Bölge: {bolge.ad} ({bolge.il})
- Nüfus: {bolge.nufus:,}

## Tahmin Kayıtları
{tahmin_satirlari}

Lütfen aşağıdaki başlıklar altında Türkçe özet rapor oluştur:
1. **Genel Özet**: Bölgedeki afet olaylarının genel bir değerlendirmesi
2. **Trend Analizi**: İhtiyaç miktarlarındaki artış/azalış eğilimleri
3. **En Kritik Olay**: Hangi olay en fazla kaynağa ihtiyaç duyuyor ve neden
4. **Ortalama İhtiyaç Profili**: Tüm olaylar ortalamasında bölgenin ihtiyaç dağılımı
5. **Stratejik Değerlendirme**: Bölgenin genel afet risk profili ve uzun vadeli öneriler
"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text

    def lojistik_onerisi_olustur(self, bolge, tahmin, afet_verisi):
        """
        Tahmin sonuçlarına dayanarak detaylı lojistik planlama
        ve kaynak dağıtım önerileri üretir.

        Args:
            bolge: Bölge nesnesi
            tahmin: TahminKaydi nesnesi
            afet_verisi: AfetOlayi nesnesi

        Returns:
            str: Gemini'nin ürettiği lojistik öneri metni
        """
        prompt = f"""Sen bir afet lojistik planlama uzmanısın. Aşağıdaki verilere dayanarak
detaylı bir lojistik ve kaynak dağıtım planı oluştur.

## Bölge Bilgileri
- Bölge: {bolge.ad}, {bolge.il}
- Nüfus: {bolge.nufus:,}
- Koordinat: {bolge.koordinat_lat or 'N/A'}, {bolge.koordinat_lon or 'N/A'}

## Afet Durumu
- Deprem Büyüklüğü: {afet_verisi.deprem_buyuklugu}
- Bina Yıkım Oranı: %{afet_verisi.bina_yikim_orani * 100:.1f}
- Hava Sıcaklığı: {afet_verisi.hava_sicakligi}°C
- Ulaşım Durumu: {_ulasim_durumu_metin(afet_verisi.ulasim_durumu)}

## Tahmini İhtiyaçlar
- Acil Barınma: {tahmin.acil_barinma} birim (çadır/konteyner)
- Gıda Paketi: {tahmin.gida} birim
- Su: {tahmin.su} birim (litre)
- Medikal Malzeme: {tahmin.medikal} birim
- Kurtarma Ekibi: {tahmin.ekip} ekip

Lütfen aşağıdaki başlıklar altında Türkçe lojistik plan oluştur:
1. **Kaynak Dağıtım Planı**: Her ihtiyaç kalemi için miktar, kaynak ve dağıtım noktası önerileri
2. **Ulaşım ve Lojistik Rotası**: Ulaşım durumuna göre alternatif erişim yolları
3. **Depolama ve Dağıtım Noktaları**: Önerilen toplanma ve dağıtım merkezi konumları
4. **Personel Planlaması**: İhtiyaç duyulan personel sayısı ve uzmanlık alanları
5. **Zamanlama**: İlk 6 saat, 6-24 saat, 24-72 saat için aşamalı plan
6. **Hava Koşulları Etkisi**: Sıcaklık ve mevsim koşullarına göre özel önlemler
"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text

    def kisa_degerlendirme_olustur(self, bolge, tahmin):
        """
        POST /predict endpoint'inin yanıtına eklenmek üzere, tahmin sonuçlarının
        en fazla 1-2 cümlelik çok kısa ve net bir özetini üretir.

        Args:
            bolge: Bölge nesnesi
            tahmin: Modelden dönen tahmin dizisi (acil_barinma, gida, su, vb.)

        Returns:
            str: 1-2 cümlelik kısa AI değerlendirme metni
        """
        prompt = f"""Sen bir kriz yöneticisisin. Aşağıdaki tahmin verisine bakarak 
en fazla 2 cümlelik, çok kısa bir acil durum değerlendirmesi yaz.

Bölge: {bolge.ad}, {bolge.il} (Nüfus: {bolge.nufus:,})
Tahminler: Barınma: {int(tahmin[0])}, Gıda: {int(tahmin[1])}, Su: {int(tahmin[2])}, Medikal: {int(tahmin[3])}, Ekip: {int(tahmin[4])}

Sadece en kritik 1-2 ihtiyacı vurgulayan acil durum cümlesi yaz. Başlık veya liste kullanma."""
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text


def _ulasim_durumu_metin(kod):
    """Ulaşım durumu kodunu okunabilir metne çevirir."""
    durumlar = {0: 'Kapalı', 1: 'Kısmi Açık', 2: 'Açık'}
    return durumlar.get(kod, 'Bilinmiyor')
