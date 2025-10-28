# YAGO v7.1 - Deployment Guide

**Created**: 2025-10-28
**Version**: 7.1.0
**Status**: Production Ready

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Development Deployment](#development-deployment)
4. [Production Deployment](#production-deployment)
5. [Environment Configuration](#environment-configuration)
6. [CI/CD Setup](#cicd-setup)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Docker**: 24.0+ & Docker Compose 2.20+
- **Python**: 3.11+
- **Node.js**: 20+
- **Git**: 2.40+

### Required API Keys
- **OpenAI API Key** (for GPT models)
- **Anthropic API Key** (for Claude models)
- **Google AI API Key** (for Gemini models)

### System Requirements

#### Development
- CPU: 2+ cores
- RAM: 4GB minimum, 8GB recommended
- Disk: 10GB free space

#### Production
- CPU: 4+ cores
- RAM: 8GB minimum, 16GB recommended
- Disk: 50GB free space
- Network: 1Gbps connection

---

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/yago.git
cd yago
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit with your API keys
nano .env
```

### 3. Start Services
```bash
# Development mode
docker-compose -f docker-compose.dev.yml up -d

# Production mode
docker-compose up -d
```

### 4. Verify Installation
```bash
# Check services are running
docker-compose ps

# Test backend API
curl http://localhost:8000/api/v1/costs/health

# Open frontend
open http://localhost:3000
```

---

## Development Deployment

### Using Docker Compose (Recommended)

```bash
# Start all services with hot reload
docker-compose -f docker-compose.dev.yml up

# Or run in background
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

### Manual Setup (Without Docker)

#### Backend
```bash
# Navigate to backend directory
cd yago/web/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Start backend server
python api.py

# Or with hot reload
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
# Navigate to frontend directory
cd yago/web/frontend

# Install dependencies
npm ci

# Start dev server
npm run dev
```

### Development Features
- Hot reload for both frontend and backend
- Source code mounted as volumes
- Debug logging enabled
- Separate development database
- CORS configured for localhost

---

## Production Deployment

### 1. Prepare Server

#### Install Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Configure Firewall
```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

### 2. Clone and Configure

```bash
# Create application directory
sudo mkdir -p /opt/yago
sudo chown $USER:$USER /opt/yago
cd /opt/yago

# Clone repository
git clone https://github.com/yourusername/yago.git .

# Configure environment
cp .env.example .env
nano .env  # Add production values
```

### 3. SSL/TLS Configuration

#### Using Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt-get install certbot

# Obtain certificate
sudo certbot certonly --standalone -d yago.yourdomain.com

# Certificates will be in:
# /etc/letsencrypt/live/yago.yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yago.yourdomain.com/privkey.pem
```

#### Configure Nginx for SSL
```bash
# Create nginx directory
mkdir -p nginx/ssl

# Copy certificates
sudo cp /etc/letsencrypt/live/yago.yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yago.yourdomain.com/privkey.pem nginx/ssl/
```

### 4. Deploy Services

```bash
# Build and start services
docker-compose up -d --build

# Verify deployment
docker-compose ps
docker-compose logs -f
```

### 5. Configure Nginx Reverse Proxy

Create `/opt/yago/nginx/nginx.conf`:

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:80;
}

server {
    listen 80;
    server_name yago.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yago.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 6. Set Up Automatic Backups

```bash
# Create backup script
cat > /opt/yago/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/opt/yago/backups
mkdir -p $BACKUP_DIR

# Backup database
docker exec yago-backend tar czf - /app/data | gzip > $BACKUP_DIR/db_$DATE.tar.gz

# Backup environment
cp /opt/yago/.env $BACKUP_DIR/env_$DATE

# Keep only last 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/yago/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/yago/backup.sh") | crontab -
```

### 7. Configure Auto-Restart

```bash
# Create systemd service
sudo tee /etc/systemd/system/yago.service << EOF
[Unit]
Description=YAGO AI Orchestrator
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/yago
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable yago.service
sudo systemctl start yago.service
```

---

## Environment Configuration

### Required Variables

```bash
# AI Provider API Keys
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-key-here

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Frontend API URL
VITE_API_BASE_URL=https://yago.yourdomain.com/api
```

### Optional Variables

```bash
# Database (PostgreSQL instead of SQLite)
DATABASE_URL=postgresql://user:password@postgres:5432/yago

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Security
SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=INFO
```

---

## CI/CD Setup

### GitHub Actions Configuration

The project includes two workflows:

1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Runs on every push and PR
   - Tests backend and frontend
   - Runs linting and type checking
   - Builds Docker images
   - Runs security scans

2. **CD Pipeline** (`.github/workflows/cd.yml`)
   - Runs on push to main branch
   - Builds and pushes Docker images
   - Deploys to production
   - Creates GitHub releases

### Required GitHub Secrets

Go to `Settings → Secrets and variables → Actions` and add:

```
PRODUCTION_HOST=your-server-ip
PRODUCTION_USER=deploy
PRODUCTION_SSH_KEY=<your-ssh-private-key>
PRODUCTION_URL=https://yago.yourdomain.com
```

### Manual Deployment

```bash
# SSH to server
ssh deploy@your-server

# Navigate to project
cd /opt/yago

# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Verify
docker-compose ps
curl https://yago.yourdomain.com/api/v1/costs/health
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/v1/costs/health

# Frontend health
curl http://localhost:3000/health

# Docker containers
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

### Resource Monitoring

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up unused images
docker image prune -a

# Clean up unused volumes
docker volume prune
```

### Database Management

```bash
# Backup database
docker exec yago-backend tar czf - /app/data > backup_$(date +%Y%m%d).tar.gz

# Restore database
cat backup_20251028.tar.gz | docker exec -i yago-backend tar xzf - -C /

# View database
docker exec -it yago-backend sqlite3 /app/data/yago.db
```

### Performance Tuning

#### Backend Scaling
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

#### Database Optimization
```bash
# Switch to PostgreSQL for better performance
# Uncomment postgres service in docker-compose.yml
docker-compose up -d postgres

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://yago:password@postgres:5432/yago
```

---

## Troubleshooting

### Common Issues

#### 1. Services Won't Start

```bash
# Check logs
docker-compose logs

# Check ports
sudo lsof -i :8000
sudo lsof -i :3000

# Restart services
docker-compose down
docker-compose up -d
```

#### 2. API Returns 500 Errors

```bash
# Check backend logs
docker-compose logs backend

# Verify environment variables
docker-compose exec backend env | grep API_KEY

# Restart backend
docker-compose restart backend
```

#### 3. Frontend Can't Connect to Backend

```bash
# Check CORS configuration
# Verify VITE_API_BASE_URL in frontend .env

# Check network
docker-compose exec frontend ping backend

# Rebuild frontend
docker-compose up -d --build frontend
```

#### 4. Database Locked

```bash
# Stop all services
docker-compose down

# Remove database lock
docker-compose exec backend rm /app/data/*.db-wal
docker-compose exec backend rm /app/data/*.db-shm

# Restart
docker-compose up -d
```

#### 5. Out of Disk Space

```bash
# Clean Docker system
docker system prune -a --volumes

# Check disk usage
df -h
du -sh /var/lib/docker

# Move Docker data directory
# Edit /etc/docker/daemon.json
{
  "data-root": "/mnt/newlocation"
}
```

### Performance Issues

#### Slow API Response

```bash
# Check CPU/Memory
docker stats

# Increase workers
# In .env: WORKERS=8

# Enable Redis caching
docker-compose up -d redis
```

#### High Memory Usage

```bash
# Limit container memory
# In docker-compose.yml:
services:
  backend:
    mem_limit: 2g
    memswap_limit: 2g
```

---

## Security Best Practices

### 1. Environment Variables
- Never commit `.env` to version control
- Use strong, unique passwords
- Rotate API keys regularly

### 2. Network Security
- Use HTTPS in production
- Configure firewall rules
- Enable fail2ban for SSH

### 3. Docker Security
- Run containers as non-root user
- Scan images for vulnerabilities
- Keep Docker updated

### 4. Application Security
- Enable rate limiting
- Validate all inputs
- Use prepared statements for database queries

---

## Updating YAGO

### Update Process

```bash
# 1. Backup current installation
./backup.sh

# 2. Pull latest changes
git pull origin main

# 3. Update dependencies
docker-compose down
docker-compose pull
docker-compose up -d --build

# 4. Verify update
curl http://localhost:8000/api/v1/costs/health
```

### Rollback Procedure

```bash
# 1. Stop services
docker-compose down

# 2. Checkout previous version
git log --oneline  # Find previous commit
git checkout <commit-hash>

# 3. Restore database
cat backup_20251028.tar.gz | docker exec -i yago-backend tar xzf - -C /

# 4. Rebuild and restart
docker-compose up -d --build
```

---

## Support

### Documentation
- [API Testing Guide](./API_TESTING.md)
- [Development Guide](./README.md)

### Get Help
- GitHub Issues: https://github.com/yourusername/yago/issues
- Email: support@yago.dev

---

**Last Updated**: 2025-10-28
**Maintainer**: YAGO Development Team
**Version**: 7.1.0
