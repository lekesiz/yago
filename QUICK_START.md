# YAGO v7.1 - Quick Start Guide

**Get YAGO running in 5 minutes!**

---

## 1. Prerequisites Check

```bash
# Check Docker
docker --version  # Should be 24.0+

# Check Docker Compose
docker-compose --version  # Should be 2.20+

# Check Git
git --version  # Should be 2.40+
```

---

## 2. Clone & Configure

```bash
# Clone repository
git clone https://github.com/yourusername/yago.git
cd yago

# Copy environment template
cp .env.example .env

# Edit with your API keys (required)
nano .env
```

**Minimum required in `.env`:**
```bash
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-key-here
```

---

## 3. Start YAGO

### Development Mode (with hot reload)
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### Production Mode
```bash
docker-compose up -d
```

---

## 4. Verify Installation

```bash
# Check services are running
docker-compose ps

# Should show:
# yago-backend    running    0.0.0.0:8000->8000/tcp
# yago-frontend   running    0.0.0.0:3000->80/tcp
# yago-redis      running    0.0.0.0:6379->6379/tcp
```

---

## 5. Test the APIs

```bash
# Backend health check
curl http://localhost:8000/api/v1/costs/health

# Should return:
# {"status":"healthy","total_projects":0,...}

# Run full test suite
chmod +x test_api_endpoints.sh
./test_api_endpoints.sh

# Should show: 92% success rate (13/14 tests passing)
```

---

## 6. Access the UI

Open in your browser:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs (Swagger UI)

---

## 7. Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Stop Services
```bash
# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Update YAGO
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

---

## Troubleshooting

### Services won't start?
```bash
# Check ports are available
sudo lsof -i :8000
sudo lsof -i :3000

# If ports are in use, kill the processes or change ports in docker-compose.yml
```

### API returns errors?
```bash
# Check backend logs
docker-compose logs backend

# Verify API keys are set
docker-compose exec backend env | grep API_KEY

# Restart backend
docker-compose restart backend
```

### Frontend can't connect?
```bash
# Check CORS settings in backend
# Verify VITE_API_BASE_URL in .env

# Rebuild frontend
docker-compose up -d --build frontend
```

---

## Next Steps

1. Read [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment
2. Read [API_TESTING.md](./API_TESTING.md) for API documentation
3. Configure CI/CD with GitHub Actions
4. Set up monitoring and backups

---

## Quick Reference

| Component | Port | URL |
|-----------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| Redis | 6379 | localhost:6379 |

---

**Need help?** Check the [full documentation](./DEPLOYMENT.md) or open an issue on GitHub.

**Last Updated**: 2025-10-28
