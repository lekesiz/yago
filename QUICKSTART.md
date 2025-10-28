# 🚀 YAGO v8.0 - 5 Dakikada Başla

**YAGO'yu lokal olarak çalıştır ve test et**

---

## ⚡ Hızlı Başlangıç

### 1. Tek Komutla Başlat

```bash
cd /Users/mikail/Desktop/YAGO
./scripts/start-local.sh
```

**İşte bu kadar!** Script otomatik olarak:
- ✅ Python bağımlılıklarını yükleyecek
- ✅ Node.js bağımlılıklarını yükleyecek
- ✅ Database'i oluşturacak
- ✅ Backend'i başlatacak (http://localhost:8000)
- ✅ Frontend'i başlatacak (http://localhost:3000)

### 2. Tarayıcıda Aç

```
http://localhost:3000
```

### 3. Test Et!

[LOCAL_SETUP.md](LOCAL_SETUP.md) dosyasındaki test senaryolarını takip et.

---

## 🛑 Durdurmak İçin

```bash
./scripts/stop-local.sh
```

---

## 📚 Detaylı Dokümantasyon

- **[LOCAL_SETUP.md](LOCAL_SETUP.md)** - Kapsamlı lokal kurulum ve test rehberi
- **[TEST_REPORT_TEMPLATE.md](TEST_REPORT_TEMPLATE.md)** - Test raporu şablonu
- **[README.md](README.md)** - Genel proje dokümantasyonu

---

## ❓ Sorun mu Yaşıyorsun?

### Backend başlamıyor

```bash
# Portları kontrol et
lsof -i :8000

# Logları kontrol et
tail -f logs/backend.log
```

### Frontend başlamıyor

```bash
# Portları kontrol et
lsof -i :3000

# Logları kontrol et
tail -f logs/frontend.log
```

### Tüm sorunlar için

[LOCAL_SETUP.md](LOCAL_SETUP.md) dosyasındaki "Sorun Giderme" bölümüne bak.

---

**Başarılar! 🎉**
