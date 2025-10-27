# 🌐 YAGO Web Dashboard

Modern, kullanıcı dostu web arayüzü ile YAGO'yu tarayıcıdan kullanın!

## 🚀 Hızlı Başlangıç

### 1. Bağımlılıkları Kur

```bash
pip install fastapi uvicorn websockets
# veya
pip install -r requirements.txt
```

### 2. Backend API'yi Başlat

```bash
cd web/backend
python api.py
```

Backend şu adreste çalışacak:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)

### 3. Frontend'i Aç

Tarayıcıda şu dosyayı aç:
```
web/frontend/index.html
```

Veya basit bir HTTP server ile:
```bash
cd web/frontend
python -m http.server 3000
```

Sonra tarayıcıda: http://localhost:3000

## ✨ Özellikler

### 📊 Dashboard Ana Sayfa
- Sistem durumu ve istatistikler
- Aktif ve tamamlanmış projeler
- Gerçek zamanlı güncelleme

### 🎨 Project Builder
- Yeni proje oluşturma
- Template seçimi
- Mod seçimi (Minimal/Full)
- Interactive mode toggle
- Auto-debug toggle

### ⚡ Live Execution View
- Real-time progress bar
- WebSocket ile canlı güncelleme
- Log görüntüleme
- Durum takibi (queued, running, completed, failed)

### 📜 History & Reports
- Geçmiş projeler listesi
- Detaylı log görüntüleme
- Proje bilgileri

### 🎯 Template Management
- Mevcut template'leri görüntüle
- Template'e göre proje oluştur
- Kategori bazlı organizasyon

## 🛠️ API Endpoints

### System Status
```http
GET /api/status
```

Response:
```json
{
  "status": "running",
  "active_projects": 2,
  "total_projects_completed": 15,
  "uptime": "3h 25m 12s"
}
```

### List Templates
```http
GET /api/templates
```

### Create Project
```http
POST /api/projects
Content-Type: application/json

{
  "idea": "Flask REST API for user management",
  "mode": "minimal",
  "template": "fastapi_rest_api",
  "interactive": false,
  "auto_debug": true
}
```

### Get Project Details
```http
GET /api/projects/{project_id}
```

### List All Projects
```http
GET /api/projects
```

### Delete Project
```http
DELETE /api/projects/{project_id}
```

## 🔌 WebSocket Connection

Real-time updates için WebSocket:

```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/${projectId}`);

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log(update);
};
```

Update types:
- `project_state`: Initial project state
- `update`: Progress updates

## 🎨 Frontend Teknolojisi

- **Framework**: React 18 (CDN)
- **Styling**: TailwindCSS (CDN)
- **State**: React Hooks
- **Build**: Babel Standalone (no build step!)

## 📝 Backend Teknolojisi

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Real-time**: WebSocket
- **CORS**: Enabled for development

## 🔧 Geliştirme

### Backend Geliştirme

```bash
# Auto-reload ile başlat
uvicorn api:app --reload --port 8000
```

### Frontend Geliştirme

`index.html` dosyasını düzenle ve tarayıcıda yenile. Build adımı yok!

## 🚀 Production Deployment

### Backend

```bash
# Gunicorn ile deploy
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app --bind 0.0.0.0:8000
```

### Frontend

- React CDN'i production sürümüne değiştir
- TailwindCSS'i build et
- CORS ayarlarını güncelle
- nginx/Apache ile servis et

## 📊 Özellik Matrisi

| Özellik | CLI | Web Dashboard |
|---------|-----|---------------|
| Proje oluşturma | ✅ | ✅ |
| Template kullanımı | ✅ | ✅ |
| Interactive mode | ✅ | 🚧 (Planned) |
| Real-time progress | ❌ | ✅ |
| Proje geçmişi | ❌ | ✅ |
| Log görüntüleme | ✅ (file) | ✅ (UI) |
| Multi-project | ❌ | ✅ |
| Visual reports | ❌ | 🚧 (Planned) |

## 🔐 Güvenlik

### Development
- CORS: Tüm originlere açık
- API Key: Yok

### Production
- CORS: Belirli domainlere kısıtla
- API Key authentication ekle
- HTTPS kullan
- Rate limiting ekle

## 🐛 Sorun Giderme

### Backend başlamıyor
```bash
# Port 8000 kullanımda mı kontrol et
lsof -i :8000

# Bağımlılıkları tekrar kur
pip install fastapi uvicorn websockets
```

### Frontend API'ye bağlanamıyor
- Backend'in çalıştığından emin ol
- CORS hatası varsa backend'de CORS ayarlarını kontrol et
- Browser console'da hata mesajlarını kontrol et

### WebSocket bağlantısı kopuyor
- Backend loglarını kontrol et
- Project ID'nin doğru olduğundan emin ol
- Network inspector'da WebSocket trafiğini kontrol et

## 📚 Daha Fazla Bilgi

- **API Dokümantasyonu**: http://localhost:8000/docs
- **YAGO Ana Döküman**: ../README.md
- **Development Roadmap**: ../DEVELOPMENT_ROADMAP.md

## 🎯 Roadmap

### v3.5 (Current)
- ✅ FastAPI backend
- ✅ React frontend
- ✅ WebSocket real-time updates
- ✅ Project management
- ✅ Template integration

### v3.6 (Planned)
- [ ] Interactive chat UI
- [ ] Visual metrics/charts
- [ ] Code diff viewer
- [ ] Multi-user support
- [ ] Authentication system
- [ ] Database persistence

### v4.0 (Future)
- [ ] Desktop app (Electron)
- [ ] VS Code extension
- [ ] Mobile app
- [ ] Cloud deployment
- [ ] Team collaboration

---

**Version**: 3.5.0
**Last Updated**: 2025-01-06
**Maintainer**: YAGO Development Team
