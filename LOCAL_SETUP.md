# 🏠 YAGO v8.0 - Lokal Kurulum ve Test Rehberi

**Lokal development ve kullanıcı testi için adım adım kılavuz**

---

## 📋 İçindekiler

- [Ön Gereksinimler](#ön-gereksinimler)
- [Hızlı Başlangıç](#hızlı-başlangıç)
- [Detaylı Kurulum](#detaylı-kurulum)
- [Test Senaryoları](#test-senaryoları)
- [Sorun Giderme](#sorun-giderme)

---

## Ön Gereksinimler

### Gerekli Yazılımlar

```bash
# Python 3.11 veya üzeri
python3 --version
# Çıktı: Python 3.11.0 veya üzeri

# Node.js 18 veya üzeri
node --version
# Çıktı: v18.0.0 veya üzeri

# npm
npm --version
# Çıktı: 9.0.0 veya üzeri

# Git
git --version
```

### Python Kurulumu (macOS)

```bash
# Homebrew ile
brew install python@3.11

# Veya pyenv ile
brew install pyenv
pyenv install 3.11.7
pyenv global 3.11.7
```

### Node.js Kurulumu (macOS)

```bash
# Homebrew ile
brew install node@18

# Veya nvm ile
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

---

## Hızlı Başlangıç

### Tek Komutla Başlat (Önerilen)

```bash
cd /Users/mikail/Desktop/YAGO
./scripts/start-local.sh
```

Bu script otomatik olarak:
- ✅ Python bağımlılıklarını yükler
- ✅ Node.js bağımlılıklarını yükler
- ✅ SQLite veritabanını oluşturur
- ✅ Backend'i başlatır (http://localhost:8000)
- ✅ Frontend'i başlatır (http://localhost:3000)

---

## Detaylı Kurulum

### 1. Repository'yi Klonla (Zaten var)

```bash
cd /Users/mikail/Desktop/YAGO
```

### 2. Python Virtual Environment Oluştur

```bash
# Virtual environment oluştur
python3 -m venv venv

# Aktive et
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 3. Environment Variables Ayarla

```bash
# .env dosyası oluştur
cp .env.example .env

# Düzenle (opsiyonel - AI API keys)
nano .env
```

**.env İçeriği** (minimum):

```bash
# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug

# Database (SQLite - otomatik oluşturulur)
DATABASE_TYPE=sqlite
DATABASE_PATH=./data/yago.db

# Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Frontend (CORS için)
FRONTEND_URL=http://localhost:3000

# AI APIs (Opsiyonel - test için gerekli değil)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=...

# JWT Secret (test için)
JWT_SECRET=test-secret-key-change-in-production
```

### 4. Backend'i Başlat

```bash
# Terminal 1
cd /Users/mikail/Desktop/YAGO
source venv/bin/activate

# Backend'i çalıştır
python -m uvicorn yago.web.backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Başarılı Çıktı**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test Et**:
```bash
curl http://localhost:8000/health
# Çıktı: {"status": "healthy"}
```

### 5. Frontend'i Başlat

```bash
# Terminal 2 (yeni terminal aç)
cd /Users/mikail/Desktop/YAGO/yago/web/frontend

# Bağımlılıkları yükle (ilk seferinde)
npm install

# Frontend'i çalıştır
npm start
```

**Başarılı Çıktı**:
```
Compiled successfully!

You can now view yago-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.x:3000
```

### 6. Tarayıcıda Aç

```
http://localhost:3000
```

---

## Test Senaryoları

### A. Temel Fonksiyonellik Testleri

#### 1. Sistem Sağlık Kontrolü

```bash
# Backend health check
curl http://localhost:8000/health

# Beklenen: {"status": "healthy"}
```

#### 2. API Dokümantasyonu

Tarayıcıda aç:
```
http://localhost:8000/docs
```

**Test Et**:
- ✅ Swagger UI açılıyor mu?
- ✅ 73 endpoint görünüyor mu?
- ✅ "Try it out" butonu çalışıyor mu?

#### 3. Kullanıcı Kaydı

**Swagger UI'da**:
1. `/api/v1/auth/register` endpoint'ini bul
2. "Try it out" butonuna tıkla
3. Body:
   ```json
   {
     "email": "test@yago.dev",
     "password": "Test123!",
     "full_name": "Test User",
     "role": "USER"
   }
   ```
4. Execute

**Beklenen Sonuç**: 200 OK, user ID dönmeli

#### 4. Giriş Yapma

1. `/api/v1/auth/login` endpoint'ini bul
2. Body:
   ```json
   {
     "email": "test@yago.dev",
     "password": "Test123!"
   }
   ```
3. Execute

**Beklenen Sonuç**: Token dönmeli
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Token'ı kaydet** - sonraki testlerde kullanılacak!

---

### B. AI Model Selection Testleri

#### 5. Model Listesi

```bash
curl http://localhost:8000/api/v1/models/list
```

**Beklenen**: 10 model listesi (GPT-4, Claude, Gemini, etc.)

#### 6. Model Seçimi (CHEAPEST)

```bash
curl -X POST http://localhost:8000/api/v1/models/select \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "CHEAPEST",
    "max_cost": 10.0,
    "min_context_window": 4000
  }'
```

**Beklenen**: `gpt-3.5-turbo` veya benzer ucuz model

#### 7. Model Seçimi (BEST_QUALITY)

```bash
curl -X POST http://localhost:8000/api/v1/models/select \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "BEST_QUALITY"
  }'
```

**Beklenen**: `gpt-4-turbo` veya `claude-3-opus`

---

### C. Auto-Healing Testleri

#### 8. Sağlık Durumu Kontrolü

```bash
curl http://localhost:8000/api/v1/healing/health
```

**Beklenen**: Tüm componentler "HEALTHY"

#### 9. Recovery İstatistikleri

```bash
curl http://localhost:8000/api/v1/healing/stats
```

**Beklenen**: Boş veya minimal istatistikler (yeni kurulumda)

---

### D. Analytics Testleri

#### 10. Metrics Toplama

```bash
curl -X POST http://localhost:8000/api/v1/analytics/record \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "metric_type": "COST",
    "value": 0.05,
    "metadata": {
      "model": "gpt-3.5-turbo",
      "tokens": 1000
    }
  }'
```

#### 11. Metrics Özeti

```bash
curl http://localhost:8000/api/v1/analytics/summary?hours=24 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 12. Cost Forecasting

```bash
curl http://localhost:8000/api/v1/analytics/forecast/cost?months=1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### E. Marketplace Testleri

#### 13. Marketplace Items

```bash
curl http://localhost:8000/api/v1/marketplace/list
```

**Beklenen**: 5 pre-registered item (Slack, GitHub, LLM, etc.)

#### 14. Item Detayları

```bash
curl http://localhost:8000/api/v1/marketplace/slack-integration
```

#### 15. Item Yükleme

```bash
curl -X POST http://localhost:8000/api/v1/marketplace/install \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "slack-integration"
  }'
```

---

### F. Frontend UI Testleri

#### 16. Ana Sayfa Yükleme
- [ ] Sayfa açılıyor mu?
- [ ] Logo görünüyor mu?
- [ ] Navigasyon çalışıyor mu?

#### 17. Login Sayfası
- [ ] Login formu görünüyor mu?
- [ ] Email validation çalışıyor mu?
- [ ] Login başarılı mı?
- [ ] Token localStorage'a kaydediliyor mu?

#### 18. Dashboard
- [ ] Dashboard yükleniyor mu?
- [ ] Kullanıcı bilgileri görünüyor mu?
- [ ] Menü itemları çalışıyor mu?

#### 19. AI Models Sayfası
- [ ] Model listesi görünüyor mu?
- [ ] Model detayları açılıyor mu?
- [ ] Model seçimi çalışıyor mu?
- [ ] Comparison tool çalışıyor mu?

#### 20. Analytics Sayfası
- [ ] Grafik görünüyor mu?
- [ ] Metrics güncelleniyor mu?
- [ ] Forecast çalışıyor mu?

#### 21. Marketplace Sayfası
- [ ] Item listesi görünüyor mu?
- [ ] Search çalışıyor mu?
- [ ] Filter çalışıyor mu?
- [ ] Install butonu çalışıyor mu?

---

## Performance Testleri

### G. Yük Testleri

#### 22. Concurrent Requests

```bash
# Apache Bench ile (opsiyonel)
ab -n 100 -c 10 http://localhost:8000/health

# Beklenen: Tüm requestler başarılı
```

#### 23. Response Time

```bash
# Ping endpoint
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/models/list

# curl-format.txt içeriği:
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_starttransfer:  %{time_starttransfer}\n
time_total:  %{time_total}\n
```

**Beklenen**: < 100ms

---

## Test Checklist

### ✅ Backend API Testleri

- [ ] Health check çalışıyor
- [ ] API docs (Swagger) açılıyor
- [ ] Kullanıcı kaydı çalışıyor
- [ ] Login çalışıyor
- [ ] Token authentication çalışıyor
- [ ] Model listesi geliyor
- [ ] Model seçimi çalışıyor (5 strateji)
- [ ] Model comparison çalışıyor
- [ ] Health monitoring çalışıyor
- [ ] Recovery stats geliyor
- [ ] Metrics toplama çalışıyor
- [ ] Analytics özeti geliyor
- [ ] Cost forecasting çalışıyor
- [ ] Anomaly detection çalışıyor
- [ ] Marketplace listesi geliyor
- [ ] Item detayları geliyor
- [ ] Item installation çalışıyor

### ✅ Frontend UI Testleri

- [ ] Ana sayfa yükleniyor
- [ ] Login sayfası çalışıyor
- [ ] Registration çalışıyor
- [ ] Dashboard yükleniyor
- [ ] Navigation çalışıyor
- [ ] AI Models sayfası çalışıyor
- [ ] Model selection çalışıyor
- [ ] Analytics sayfası çalışıyor
- [ ] Grafik görselleştirme çalışıyor
- [ ] Marketplace sayfası çalışıyor
- [ ] Search/filter çalışıyor
- [ ] Responsive design çalışıyor

### ✅ Integration Testleri

- [ ] Frontend → Backend iletişimi
- [ ] Authentication flow
- [ ] CORS çalışıyor
- [ ] WebSocket (varsa) çalışıyor
- [ ] File upload (varsa) çalışıyor
- [ ] Error handling çalışıyor

### ✅ Security Testleri

- [ ] JWT token doğrulaması
- [ ] Password hashing
- [ ] CORS ayarları
- [ ] Rate limiting (varsa)
- [ ] SQL injection koruması
- [ ] XSS koruması

### ✅ Performance Testleri

- [ ] Sayfa yükleme < 2 saniye
- [ ] API response < 100ms
- [ ] 100 concurrent request desteği
- [ ] Memory leak yok
- [ ] CPU kullanımı normal

---

## Sorun Giderme

### Backend Başlatılamıyor

**Hata**: `Address already in use`

**Çözüm**:
```bash
# Port 8000'i kullanan process'i bul
lsof -i :8000

# Kill et
kill -9 <PID>
```

### Frontend Başlatılamıyor

**Hata**: `EADDRINUSE: address already in use :::3000`

**Çözüm**:
```bash
# Port 3000'i kullanan process'i bul
lsof -i :3000

# Kill et
kill -9 <PID>

# Veya farklı port kullan
PORT=3001 npm start
```

### Database Hatası

**Hata**: `OperationalError: unable to open database file`

**Çözüm**:
```bash
# data klasörünü oluştur
mkdir -p /Users/mikail/Desktop/YAGO/data

# İzinleri kontrol et
chmod 755 /Users/mikail/Desktop/YAGO/data
```

### Python Dependency Hatası

**Hata**: `ModuleNotFoundError: No module named 'xxx'`

**Çözüm**:
```bash
# Virtual environment aktive et
source venv/bin/activate

# Bağımlılıkları tekrar yükle
pip install -r requirements.txt --force-reinstall
```

### CORS Hatası

**Hata**: `Access-Control-Allow-Origin`

**Çözüm**:
`.env` dosyasında kontrol et:
```bash
FRONTEND_URL=http://localhost:3000
```

Backend'de CORS ayarlarını kontrol et:
```python
# yago/web/backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Yararlı Komutlar

### Log Takibi

```bash
# Backend logs
tail -f logs/yago.log

# Veya console'da
python -m uvicorn yago.web.backend.main:app --reload --log-level debug
```

### Database Sıfırlama

```bash
# SQLite database'i sil
rm data/yago.db

# Backend tekrar başlat (otomatik oluşturur)
python -m uvicorn yago.web.backend.main:app --reload
```

### Cache Temizleme

```bash
# Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Node.js cache
cd yago/web/frontend
rm -rf node_modules package-lock.json
npm install
```

---

## Lokal Kullanım için API Örnekleri

### Python Client Örneği

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Login
response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
    "email": "test@yago.dev",
    "password": "Test123!"
})
token = response.json()["access_token"]

# Headers
headers = {"Authorization": f"Bearer {token}"}

# Model seç
response = requests.post(
    f"{BASE_URL}/api/v1/models/select",
    json={"strategy": "BALANCED"},
    headers=headers
)
model_id = response.json()["model_id"]
print(f"Selected model: {model_id}")

# Workflow oluştur
response = requests.post(
    f"{BASE_URL}/api/v1/workflows/create",
    json={
        "name": "Test Workflow",
        "model_id": model_id,
        "prompt": "Hello, world!"
    },
    headers=headers
)
workflow_id = response.json()["workflow_id"]
print(f"Workflow created: {workflow_id}")
```

### JavaScript Client Örneği

```javascript
const BASE_URL = "http://localhost:8000";

// Login
async function login() {
  const response = await fetch(`${BASE_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: "test@yago.dev",
      password: "Test123!"
    })
  });
  const data = await response.json();
  return data.access_token;
}

// Model seç
async function selectModel(token) {
  const response = await fetch(`${BASE_URL}/api/v1/models/select`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ strategy: "BALANCED" })
  });
  const data = await response.json();
  return data.model_id;
}

// Kullanım
(async () => {
  const token = await login();
  const modelId = await selectModel(token);
  console.log(`Selected model: ${modelId}`);
})();
```

---

## Test Sonuçlarını Kaydetme

Her test sonrası bu şablonu doldur:

```markdown
# Test Raporu - [Tarih]

## Ortam
- OS: macOS 14.x
- Python: 3.11.x
- Node: 18.x
- Browser: Chrome/Safari/Firefox

## Test Sonuçları

### Backend API (17/17)
- [x] Health check
- [x] User registration
- [x] Login
- [x] Model selection
- ... (tümünü işaretle)

### Frontend UI (12/12)
- [x] Login sayfası
- [x] Dashboard
- ... (tümünü işaretle)

### Bulunan Hatalar
1. Hata açıklaması
   - Adımlar: ...
   - Beklenen: ...
   - Gerçekleşen: ...
   - Çözüm: ...

### Performans
- Ortalama response time: XX ms
- Concurrent users: XX
- Memory kullanımı: XX MB

### Notlar
- ...
```

---

## Yardım ve Destek

- **Dokümantasyon**: [README.md](README.md)
- **API Docs**: http://localhost:8000/docs
- **GitHub Issues**: https://github.com/lekesiz/yago/issues

---

**Başarılar! 🚀**

Lokal testler tamamlandıktan sonra production deployment için [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) dosyasına bakabilirsin.
