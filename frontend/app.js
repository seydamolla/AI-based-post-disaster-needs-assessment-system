// API URL
const API_BASE_URL = 'https://afet-bf7c.onrender.com';

// DOM Elements
const sidebar = document.getElementById('sidebar');
const closeSidebarBtn = document.getElementById('closeSidebarBtn');
const selectedCityName = document.getElementById('selectedCityName');
const predictBtn = document.getElementById('predictBtn');
const predictLoader = document.getElementById('predictLoader');
const resultsContainer = document.getElementById('resultsContainer');
const aiSummaryText = document.getElementById('aiSummaryText');
const fullReportBtn = document.getElementById('fullReportBtn');
const reportModal = document.getElementById('reportModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const fullReportContent = document.getElementById('fullReportContent');
const randomScenarioBtn = document.getElementById('randomScenarioBtn');

// State
let selectedProvinceId = null;
let currentPredictionId = null;

// Initialize Map
const map = L.map('map', {
    zoomControl: false, // Sağ alta alacağız
    attributionControl: false
}).setView([39.0, 35.0], 6); // Türkiye Merkezi

// Zoom kontrolünü sağ alta ekle
L.control.zoom({ position: 'bottomright' }).addTo(map);

// Koyu tema harita (CartoDB Dark Matter)
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    subdomains: 'abcd',
    maxZoom: 10,
    minZoom: 5
}).addTo(map);

// GeoJSON Layer'ı
let geojsonLayer;

// Şehir Listesi (API'deki ID'lerle eşleştirmek için)
let apiCities = [];

// API'den Bölgeleri Çek ve GeoJSON ile Eşleştir
async function initMap() {
    try {
        // 1. Doğrudan JS dosyasından GeoJSON objesini kullan (CORS hatası engellenir)
        // Haritaya Çiz
        geojsonLayer = L.geoJSON(turkeyGeoJson, {
            style: getFeatureStyle,
            onEachFeature: onEachFeature
        }).addTo(map);

        // 2. API'den kayıtlı bölgeleri al (CORS hatası alsa bile harita bozulmaz)
        try {
            const apiRes = await axios.get(`${API_BASE_URL}/bolge`);
            apiCities = apiRes.data;
        } catch (apiError) {
            console.warn("API'ye bağlanılamadı (Muhtemelen CORS hatası):", apiError.message);
            // Uyarı göster
            document.querySelector('.header-title p').textContent += " (API Bağlantı Hatası!)";
            document.querySelector('.header-title p').style.color = "#bd4343ff";
        }

    } catch (error) {
        console.error("Harita verileri (turkey.json) yüklenirken hata oluştu:", error);
    }
}

// İl sınırları stili
function getFeatureStyle(feature) {
    return {
        fillColor: '#1e293b',
        weight: 1.5,
        opacity: 1,
        color: '#3b82f6', // Mavi neon sınırlar
        dashArray: '3',
        fillOpacity: 0.4
    };
}

// İllere Hover ve Click Eklentileri
function onEachFeature(feature, layer) {
    layer.on({
        mouseover: (e) => {
            const layer = e.target;
            layer.setStyle({
                fillColor: '#3b82f6',
                fillOpacity: 0.7,
                color: '#60a5fa',
                weight: 2
            });
            layer.bringToFront();
        },
        mouseout: (e) => {
            geojsonLayer.resetStyle(e.target);
            // Eğer seçiliyse mavi kalmaya devam etmeli ama şimdilik resetliyoruz.
        },
        click: (e) => {
            // Tıklanan İlin adını al
            const cityName = feature.properties.name;
            openSidebar(cityName);
        }
    });
}

// İl Nüfusları (Kısmi liste, olmayanlar için varsayılan 500 bin kullanılacak)
const cityPopulations = {
    "İstanbul": 15840900, "Ankara": 5747325, "İzmir": 4425789, "Bursa": 3147818, "Antalya": 2619832,
    "Konya": 2277017, "Adana": 2258718, "Şanlıurfa": 2143020, "Gaziantep": 2130432, "Kocaeli": 2033441,
    "Mersin": 1891145, "Diyarbakır": 1791373, "Hatay": 1670712, "Manisa": 1456626, "Kayseri": 1434357,
    "Mardin": 862757, "Kahramanmaraş": 1171298, "Erzurum": 756893, "Van": 1141015, "Malatya": 808692
};

// Sidebar Yönetimi
function openSidebar(cityName) {
    selectedCityName.textContent = cityName;

    // Türkçe karakterleri eşleştirebilmek için küçük harfe çevirip arıyoruz
    const apiCity = apiCities.find(c =>
        c.il.toLowerCase() === cityName.toLowerCase() ||
        cityName.toLowerCase().includes(c.il.toLowerCase())
    );

    if (apiCity) {
        selectedProvinceId = apiCity.id;
    } else {
        // Veritabanında yoksa null bırakıyoruz, Analiz tuşuna basıldığında otomatik oluşturacağız.
        selectedProvinceId = null;
    }

    sidebar.classList.remove('hidden');
    resultsContainer.classList.add('hidden');
    aiSummaryText.innerHTML = "Bekleniyor...";
}

closeSidebarBtn.addEventListener('click', () => {
    sidebar.classList.add('hidden');
});

// Rastgele Senaryo Üretici
randomScenarioBtn.addEventListener('click', () => {
    // Şiddet (4.0 ile 8.0 arası)
    let mag = (Math.random() * (8.0 - 4.0) + 4.0);
    document.getElementById('depremBuyuklugu').value = mag.toFixed(1);

    // Yıkım oranı gerçekçi olmalı (sadece şiddet yüksekse yıkım olur)
    let yikim = Math.max(0, Math.pow(mag - 4.0, 3) / 100);
    // Rastgelelik ekle (bazı yerlerde binalar sağlamdır, bazı yerlerde çürüktür)
    yikim = yikim * (Math.random() * 1.5 + 0.5);
    if (yikim > 0.85) yikim = 0.85;

    document.getElementById('binaYikimOrani').value = yikim.toFixed(2);
    document.getElementById('havaSicakligi').value = (Math.random() * (35 - (-5)) + (-5)).toFixed(1);
    document.getElementById('ulasimDurumu').value = Math.floor(Math.random() * 3);
    document.getElementById('yasliNufus').value = (Math.random() * (0.25 - 0.05) + 0.05).toFixed(2);

    // Ufak bir animasyon efekti
    randomScenarioBtn.textContent = "✅ Senaryo Hazır!";
    setTimeout(() => randomScenarioBtn.textContent = "🎲 Rastgele Senaryo Doldur", 1500);
});

// Tahmin (Predict) İşlemi
predictBtn.addEventListener('click', async () => {
    const cityName = selectedCityName.textContent;

    // UI Güncelleme
    const btnText = predictBtn.querySelector('.btn-text');
    btnText.textContent = "Analiz Ediliyor...";
    predictLoader.classList.remove('hidden');
    predictBtn.disabled = true;

    try {
        // EĞER SEÇİLEN ŞEHİR VERİTABANINDA YOKSA, ÖNCE ONU KAYDET
        if (!selectedProvinceId) {
            console.log(`${cityName} veritabanında yok, oluşturuluyor...`);
            const nufus = cityPopulations[cityName] || 500000; // Listede yoksa 500 bin

            const bolgeRes = await axios.post(`${API_BASE_URL}/bolge`, {
                ad: cityName + " Merkez",
                il: cityName,
                nufus: nufus
            });

            selectedProvinceId = bolgeRes.data.bolge_id;

            // Listeyi de güncelleyelim ki bir daha tıklandığında tekrar oluşturmasın
            apiCities.push({
                id: selectedProvinceId,
                ad: cityName + " Merkez",
                il: cityName,
                nufus: nufus
            });
        }

        // Artık selectedProvinceId kesinlikle var, tahmini başlat
        const payload = {
            bolge_id: selectedProvinceId,
            deprem_buyuklugu: parseFloat(document.getElementById('depremBuyuklugu').value),
            bina_yikim_orani: parseFloat(document.getElementById('binaYikimOrani').value),
            hava_sicakligi: parseFloat(document.getElementById('havaSicakligi').value),
            ulasim_durumu: parseInt(document.getElementById('ulasimDurumu').value),
            yasli_nufus_orani: parseFloat(document.getElementById('yasliNufus').value)
        };

        const response = await axios.post(`${API_BASE_URL}/predict`, payload);
        const data = response.data;

        currentPredictionId = data.afet_olayi_id;

        // Sonuçları Doldur
        document.getElementById('resSu').textContent = data.sonuclar.su.toLocaleString();
        document.getElementById('resGida').textContent = data.sonuclar.gida.toLocaleString();
        document.getElementById('resBarinma').textContent = data.sonuclar.acil_barinma.toLocaleString();
        document.getElementById('resMedikal').textContent = data.sonuclar.medikal.toLocaleString();
        document.getElementById('resEkip').textContent = data.sonuclar.ekip.toLocaleString();

        // Yapay Zekâ Kısa Özeti
        resultsContainer.classList.remove('hidden');
        typeWriterEffect(aiSummaryText, data.ai_ozet || "Yapay zekâ özeti alınamadı.", 30);

    } catch (error) {
        console.error("Tahmin Hatası:", error);
        alert("Tahmin oluşturulurken bir hata oluştu.");
    } finally {
        btnText.textContent = "AI ile Analiz Et";
        predictLoader.classList.add('hidden');
        predictBtn.disabled = false;
    }
});

// Kapsamlı Rapor (Full Report) İşlemi
fullReportBtn.addEventListener('click', async () => {
    if (!currentPredictionId) return;

    fullReportContent.innerHTML = "<div style='text-align:center;'><span class='loader' style='border-color: #3b82f6; border-bottom-color: transparent;'></span><br><br>Yapay Zekâ raporu hazırlıyor, lütfen bekleyin...</div>";
    reportModal.classList.remove('hidden');

    try {
        const response = await axios.post(`${API_BASE_URL}/ai/analiz`, {
            afet_olayi_id: currentPredictionId
        });

        const rawMarkdown = response.data.analiz_raporu || response.data.message;
        // Markdown'u HTML'e çevir
        fullReportContent.innerHTML = marked.parse(rawMarkdown);

    } catch (error) {
        console.error("Rapor Hatası:", error);
        fullReportContent.innerHTML = "<p style='color:#ef4444'>Rapor oluşturulurken bir hata meydana geldi.</p>";
    }
});

// Modal Kapatma
closeModalBtn.addEventListener('click', () => {
    reportModal.classList.add('hidden');
});

reportModal.addEventListener('click', (e) => {
    if (e.target === reportModal) {
        reportModal.classList.add('hidden');
    }
});

// Daktilo Efekti (Typewriter Effect)
function typeWriterEffect(element, text, speed) {
    element.innerHTML = "";
    let i = 0;

    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}

// Uygulamayı Başlat
initMap();
