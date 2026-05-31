"""
Gemini API Servis ve Endpoint Testleri
======================================
Gemini API çağrılarını mocklayarak servis metotlarının doğru çalıştığını
ve API endpoint'lerinin doğru HTTP yanıtları döndüğünü test eder.

Kota tüketmemek için tüm Gemini çağrıları mocklanmıştır.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone


# ---------- Yardımcı Fonksiyonlar ----------

def _bolge_olustur(client):
    """Test için bir bölge oluşturur."""
    bolge_data = {
        "ad": "Test Bölgesi",
        "il": "Hatay",
        "ilce": "Antakya",
        "nufus": 100000,
        "koordinat_lat": 36.2,
        "koordinat_lon": 36.16
    }
    return client.post('/bolge', json=bolge_data)


def _tahmin_olustur(client, bolge_id):
    """Test için bir tahmin oluşturur."""
    predict_data = {
        "bolge_id": bolge_id,
        "deprem_buyuklugu": 7.2,
        "bina_yikim_orani": 0.65,
        "hava_sicakligi": -3.0,
        "ulasim_durumu": 0,
        "yasli_nufus_orani": 0.18
    }
    response = client.post('/predict', json=predict_data)
    assert response.status_code == 200, response.get_json()
    return response


# ==================== GeminiService Birim Testleri ====================

class TestGeminiService:
    """GeminiService sınıfının metotlarını mocklanmış API ile test eder."""

    @patch('gemini_service.genai')
    def test_gemini_service_init(self, mock_genai):
        """GeminiService'in API key ile başlatılabildiğini doğrular."""
        from gemini_service import GeminiService
        service = GeminiService(api_key='test-api-key')
        mock_genai.Client.assert_called_once_with(api_key='test-api-key')
        assert service.client is not None

    def test_gemini_service_no_api_key(self, monkeypatch):
        """API key olmadan GeminiService oluşturulduğunda ValueError fırlatıldığını doğrular."""
        monkeypatch.delenv('GEMINI_API_KEY', raising=False)
        from gemini_service import GeminiService
        with pytest.raises(ValueError, match="GEMINI_API_KEY"):
            GeminiService(api_key=None)

    @patch('gemini_service.genai')
    def test_analiz_raporu_olustur(self, mock_genai):
        """analiz_raporu_olustur metodunun doğru çalıştığını doğrular."""
        from gemini_service import GeminiService

        # Mock client ve response
        mock_response = MagicMock()
        mock_response.text = "Test analiz raporu içeriği"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        service = GeminiService(api_key='test-key')

        # Mock domain objects
        bolge = MagicMock(ad="Test", il="Hatay", ilce="Antakya", nufus=100000)
        tahmin = MagicMock(acil_barinma=500, gida=1200, su=3000, medikal=200, ekip=15)
        afet = MagicMock(deprem_buyuklugu=7.2, bina_yikim_orani=0.65,
                         hava_sicakligi=-3, ulasim_durumu=0, yasli_nufus_orani=0.18)

        rapor = service.analiz_raporu_olustur(bolge, tahmin, afet)

        assert rapor == "Test analiz raporu içeriği"
        mock_client.models.generate_content.assert_called_once()
        # Prompt'un doğru verileri içerdiğini kontrol et
        call_kwargs = mock_client.models.generate_content.call_args
        prompt_arg = call_kwargs.kwargs.get('contents') or call_kwargs[1].get('contents')
        assert "Test" in prompt_arg
        assert "Hatay" in prompt_arg
        assert "7.2" in prompt_arg

    @patch('gemini_service.genai')
    def test_tahminleri_ozetle(self, mock_genai):
        """tahminleri_ozetle metodunun doğru çalıştığını doğrular."""
        from gemini_service import GeminiService

        mock_response = MagicMock()
        mock_response.text = "Test özet raporu"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        service = GeminiService(api_key='test-key')

        bolge = MagicMock(ad="Test", il="Hatay", nufus=100000)

        # Birden fazla tahmin oluştur
        tahmin1 = MagicMock(
            acil_barinma=500, gida=1200, su=3000, medikal=200, ekip=15,
            kayit_tarihi=datetime(2025, 2, 6, 10, 30, tzinfo=timezone.utc)
        )
        tahmin1.afet_olayi = MagicMock(deprem_buyuklugu=7.2)

        tahmin2 = MagicMock(
            acil_barinma=300, gida=800, su=2000, medikal=100, ekip=10,
            kayit_tarihi=datetime(2025, 3, 15, 14, 0, tzinfo=timezone.utc)
        )
        tahmin2.afet_olayi = MagicMock(deprem_buyuklugu=5.5)

        ozet = service.tahminleri_ozetle(bolge, [tahmin1, tahmin2])

        assert ozet == "Test özet raporu"
        mock_client.models.generate_content.assert_called_once()

    @patch('gemini_service.genai')
    def test_lojistik_onerisi_olustur(self, mock_genai):
        """lojistik_onerisi_olustur metodunun doğru çalıştığını doğrular."""
        from gemini_service import GeminiService

        mock_response = MagicMock()
        mock_response.text = "Test lojistik önerisi"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        service = GeminiService(api_key='test-key')

        bolge = MagicMock(ad="Test", il="Hatay", nufus=100000,
                          koordinat_lat=36.2, koordinat_lon=36.16)
        tahmin = MagicMock(acil_barinma=500, gida=1200, su=3000, medikal=200, ekip=15)
        afet = MagicMock(deprem_buyuklugu=7.2, bina_yikim_orani=0.65,
                         hava_sicakligi=-3, ulasim_durumu=0)

        oneri = service.lojistik_onerisi_olustur(bolge, tahmin, afet)

        assert oneri == "Test lojistik önerisi"
        mock_client.models.generate_content.assert_called_once()

    @patch('gemini_service.genai')
    def test_kisa_degerlendirme_olustur(self, mock_genai):
        """kisa_degerlendirme_olustur metodunun doğru çalıştığını doğrular."""
        from gemini_service import GeminiService

        mock_response = MagicMock()
        mock_response.text = "Test kısa özet"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        service = GeminiService(api_key='test-key')
        bolge = MagicMock(ad="Test", il="Hatay", nufus=100000)
        tahmin = [500, 1200, 3000, 200, 15]

        ozet = service.kisa_degerlendirme_olustur(bolge, tahmin)

        assert ozet == "Test kısa özet"
        mock_client.models.generate_content.assert_called_once()

# ==================== Yardımcı Fonksiyon Testi ====================

def test_ulasim_durumu_metin():
    """_ulasim_durumu_metin yardımcı fonksiyonunun doğru çeviri yaptığını doğrular."""
    from gemini_service import _ulasim_durumu_metin
    assert _ulasim_durumu_metin(0) == 'Kapalı'
    assert _ulasim_durumu_metin(1) == 'Kısmi Açık'
    assert _ulasim_durumu_metin(2) == 'Açık'
    assert _ulasim_durumu_metin(99) == 'Bilinmiyor'


# ==================== API Endpoint Testleri ====================

class TestAiAnalizEndpoint:
    """POST /ai/analiz endpoint testleri."""

    @patch('api.gemini_service')
    def test_ai_analiz_success(self, mock_gemini, client):
        """Geçerli afet_olayi_id ile analiz raporu döndüğünü doğrular."""
        mock_gemini.kisa_degerlendirme_olustur.return_value = "Mock özet"
        # Önce veri oluştur
        bolge_resp = _bolge_olustur(client)
        bolge_id = bolge_resp.get_json()['bolge_id']
        predict_resp = _tahmin_olustur(client, bolge_id)
        afet_olayi_id = predict_resp.get_json()['afet_olayi_id']

        mock_gemini.analiz_raporu_olustur.return_value = "Kapsamlı analiz raporu metni"

        response = client.post('/ai/analiz', json={'afet_olayi_id': afet_olayi_id})
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert 'analiz_raporu' in json_data
        assert json_data['analiz_raporu'] == "Kapsamlı analiz raporu metni"
        assert 'bolge' in json_data
        assert 'tahmin' in json_data

    def test_ai_analiz_missing_param(self, client):
        """Eksik parametre ile 400 döndüğünü doğrular."""
        response = client.post('/ai/analiz', json={})
        assert response.status_code == 400

    @patch('api.gemini_service')
    def test_ai_analiz_not_found(self, mock_gemini, client):
        """Var olmayan afet_olayi_id ile 404 döndüğünü doğrular."""
        response = client.post('/ai/analiz', json={'afet_olayi_id': 9999})
        assert response.status_code == 404

    @patch('api.gemini_service')
    def test_ai_analiz_gemini_error(self, mock_gemini, client):
        """Gemini API hatası durumunda graceful fallback (200) döndüğünü doğrular."""
        mock_gemini.kisa_degerlendirme_olustur.return_value = "Mock özet"
        bolge_resp = _bolge_olustur(client)
        bolge_id = bolge_resp.get_json()['bolge_id']
        predict_resp = _tahmin_olustur(client, bolge_id)
        afet_olayi_id = predict_resp.get_json()['afet_olayi_id']

        mock_gemini.analiz_raporu_olustur.side_effect = Exception("API bağlantı hatası")

        response = client.post('/ai/analiz', json={'afet_olayi_id': afet_olayi_id})
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert 'Geçici Olarak Kullanılamıyor' in json_data['analiz_raporu']


class TestAiOzetleEndpoint:
    """POST /ai/ozetle endpoint testleri."""

    @patch('api.gemini_service')
    def test_ai_ozetle_success(self, mock_gemini, client):
        """Geçerli bolge_id ile özet raporu döndüğünü doğrular."""
        mock_gemini.kisa_degerlendirme_olustur.return_value = "Mock özet"
        bolge_resp = _bolge_olustur(client)
        bolge_id = bolge_resp.get_json()['bolge_id']
        _tahmin_olustur(client, bolge_id)

        mock_gemini.tahminleri_ozetle.return_value = "Özet rapor metni"

        response = client.post('/ai/ozetle', json={'bolge_id': bolge_id})
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert json_data['ozet_raporu'] == "Özet rapor metni"
        assert json_data['tahmin_sayisi'] >= 1

    def test_ai_ozetle_missing_param(self, client):
        """Eksik parametre ile 400 döndüğünü doğrular."""
        response = client.post('/ai/ozetle', json={})
        assert response.status_code == 400

    @patch('api.gemini_service')
    def test_ai_ozetle_bolge_not_found(self, mock_gemini, client):
        """Var olmayan bolge_id ile 404 döndüğünü doğrular."""
        response = client.post('/ai/ozetle', json={'bolge_id': 9999})
        assert response.status_code == 404

    @patch('api.gemini_service')
    def test_ai_ozetle_no_tahmin(self, mock_gemini, client):
        """Tahmin kaydı olmayan bölge için 404 döndüğünü doğrular."""
        bolge_resp = _bolge_olustur(client)
        bolge_id = bolge_resp.get_json()['bolge_id']
        # Tahmin oluşturmadan doğrudan özetle
        response = client.post('/ai/ozetle', json={'bolge_id': bolge_id})
        assert response.status_code == 404


class TestAiOneriEndpoint:
    """POST /ai/oneri endpoint testleri."""

    @patch('api.gemini_service')
    def test_ai_oneri_success(self, mock_gemini, client):
        """Geçerli afet_olayi_id ile lojistik önerisi döndüğünü doğrular."""
        mock_gemini.kisa_degerlendirme_olustur.return_value = "Mock özet"
        bolge_resp = _bolge_olustur(client)
        bolge_id = bolge_resp.get_json()['bolge_id']
        predict_resp = _tahmin_olustur(client, bolge_id)
        afet_olayi_id = predict_resp.get_json()['afet_olayi_id']

        mock_gemini.lojistik_onerisi_olustur.return_value = "Lojistik öneri metni"

        response = client.post('/ai/oneri', json={'afet_olayi_id': afet_olayi_id})
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert json_data['lojistik_onerisi'] == "Lojistik öneri metni"
        assert 'bolge' in json_data
        assert 'tahmin' in json_data

    def test_ai_oneri_missing_param(self, client):
        """Eksik parametre ile 400 döndüğünü doğrular."""
        response = client.post('/ai/oneri', json={})
        assert response.status_code == 400

    @patch('api.gemini_service')
    def test_ai_oneri_not_found(self, mock_gemini, client):
        """Var olmayan afet_olayi_id ile 404 döndüğünü doğrular."""
        response = client.post('/ai/oneri', json={'afet_olayi_id': 9999})
        assert response.status_code == 404
