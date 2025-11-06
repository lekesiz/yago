# 🚀 YAGO v8.4 - Production Deployment Guide

Complete guide for deploying YAGO v8.4 with all Sprint 1-5 enhancements to production.

**Version:** 8.4.0  
**Last Updated:** November 6, 2025  
**Includes:** Security fixes, Performance optimizations, Testing, API pagination, Documentation

---

## 📋 Quick Navigation

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Database Configuration](#database-configuration)
- [Backend Deployment](#backend-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Nginx Setup](#nginx-setup)
- [SSL Configuration](#ssl-configuration)
- [Monitoring](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

**Backend:**
- Python 3.11+
- PostgreSQL 14+ (Production) / SQLite 3.35+ (Development)
- Redis 7+ (Optional, for caching)

**Frontend:**
- Node.js 18.0+
- npm 9.0+ or yarn 1.22+

**Server:**
- Ubuntu 22.04 LTS or similar
- Nginx 1.22+
- Minimum 2GB RAM, 4GB recommended
- 20GB disk space

### Required API Keys

At least ONE AI provider key required:
- OpenAI API Key (`OPENAI_API_KEY`)
- Anthropic API Key (`ANTHROPIC_API_KEY`)
- Google AI API Key (`GOOGLE_API_KEY`)
- Cursor API Key (`CURSOR_API_KEY`)

---

## Environment Setup

### Backend `.env` Configuration

Create `/yago/web/backend/.env`:

\`\`\`bash
# Environment (CRITICAL)
ENV=production

# Security (Sprint 1)
JWT_SECRET_KEY=<openssl rand -hex 32>
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/yago_prod

# AI Providers (at least one required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
CURSOR_API_KEY=...

# Performance (Sprint 2)
RATE_LIMIT_ENABLED=true
CACHE_ENABLED=true
CACHE_TTL=300

# Logging (Sprint 2)
LOG_LEVEL=INFO
LOG_FILE=/var/log/yago/app.log
\`\`\`

**Generate Secure JWT Secret:**
\`\`\`bash
openssl rand -hex 32
\`\`\`

### Frontend `.env.production`

Create `/yago/web/frontend/.env.production`:

\`\`\`bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_WS_BASE_URL=wss://api.yourdomain.com
VITE_APP_VERSION=8.4.0
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_ERROR_REPORTING=true
VITE_ENABLE_DEBUG=false
\`\`\`

---

## Database Configuration

### Install PostgreSQL

\`\`\`bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql
\`\`\`

### Create Database

\`\`\`bash
sudo -u postgres psql
\`\`\`

\`\`\`sql
CREATE DATABASE yago_prod;
CREATE USER yago_user WITH ENCRYPTED PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE yago_prod TO yago_user;
\\q
\`\`\`

### Run Migrations

\`\`\`bash
cd /path/to/yago/web/backend
pip install alembic
alembic upgrade head
\`\`\`

### Verify Performance Indexes (Sprint 1)

\`\`\`sql
-- Connect to database
psql -U yago_user -d yago_prod

-- Check critical indexes
\\di

-- Should include:
-- idx_projects_user_status
-- idx_errors_resolved_severity
-- idx_usage_provider_created
-- idx_templates_category_status
-- idx_clarifications_completed
\`\`\`

---

## Backend Deployment

### Install Dependencies

\`\`\`bash
cd /path/to/yago/web/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
pip install gunicorn
\`\`\`

### Create Systemd Service

\`\`\`bash
sudo nano /etc/systemd/system/yago-backend.service
\`\`\`

\`\`\`ini
[Unit]
Description=YAGO v8.4 Backend API
After=network.target postgresql.service

[Service]
Type=notify
User=yago
Group=yago
WorkingDirectory=/path/to/yago/web/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn main:app \\
    --workers 4 \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --bind 0.0.0.0:8000 \\
    --access-logfile /var/log/yago/access.log \\
    --error-logfile /var/log/yago/error.log \\
    --log-level info \\
    --timeout 120
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
\`\`\`

### Start Backend Service

\`\`\`bash
# Create log directory
sudo mkdir -p /var/log/yago
sudo chown yago:yago /var/log/yago

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable yago-backend
sudo systemctl start yago-backend
sudo systemctl status yago-backend
\`\`\`

---

## Frontend Deployment

### Build Production Bundle

\`\`\`bash
cd /path/to/yago/web/frontend

# Install dependencies
npm install

# Build
npm run build

# Output in ./dist
ls -la dist/
\`\`\`

### Deploy Static Files

\`\`\`bash
# Create web directory
sudo mkdir -p /var/www/yago
sudo cp -r dist/* /var/www/yago/
sudo chown -R www-data:www-data /var/www/yago
\`\`\`

---

## Nginx Setup

### Install Nginx

\`\`\`bash
sudo apt install nginx
sudo systemctl enable nginx
\`\`\`

### Configure Site

Create `/etc/nginx/sites-available/yago`:

\`\`\`nginx
upstream yago_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com api.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com;

    # SSL (managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Frontend
    root /var/www/yago;
    index index.html;

    # Security headers (Sprint 1)
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # API proxy
    location /api/ {
        proxy_pass http://yago_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        
        # Rate limiting (Sprint 2)
        limit_req zone=api burst=10 nodelay;
    }

    # WebSocket proxy
    location /ws/ {
        proxy_pass http://yago_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
    }

    # Frontend routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Rate limiting zones (Sprint 2)
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
\`\`\`

### Enable Site

\`\`\`bash
sudo ln -s /etc/nginx/sites-available/yago /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
\`\`\`

---

## SSL Configuration

### Using Let's Encrypt

\`\`\`bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Test renewal
sudo certbot renew --dry-run
\`\`\`

---

## Monitoring and Logging

### Application Logs

\`\`\`bash
# Backend logs
sudo journalctl -u yago-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Application logs
sudo tail -f /var/log/yago/app.log
\`\`\`

### Error Tracking (Sprint 3)

Access error dashboard:
\`\`\`
https://yourdomain.com/admin/errors
\`\`\`

Query error stats via API:
\`\`\`bash
curl https://api.yourdomain.com/api/v1/errors/stats?hours=24
\`\`\`

### Performance Metrics (Sprint 4)

Check API metrics:
\`\`\`bash
curl https://api.yourdomain.com/api/v1/analytics?time_range=7d
\`\`\`

### Health Checks

\`\`\`bash
# API health
curl https://api.yourdomain.com/health

# Database health
psql -U yago_user -d yago_prod -c "SELECT 1;"
\`\`\`

---

## Backup Strategy

### Database Backups

Create `/usr/local/bin/backup-yago.sh`:

\`\`\`bash
#!/bin/bash
BACKUP_DIR="/backups/yago"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U yago_user yago_prod | gzip > $BACKUP_DIR/db_$TIMESTAMP.sql.gz

# Keep last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
\`\`\`

\`\`\`bash
chmod +x /usr/local/bin/backup-yago.sh

# Schedule daily backups (2 AM)
sudo crontab -e
0 2 * * * /usr/local/bin/backup-yago.sh
\`\`\`

---

## Troubleshooting

### Backend Not Starting

\`\`\`bash
# Check logs
sudo journalctl -u yago-backend -n 100

# Test manually
cd /path/to/yago/web/backend
source venv/bin/activate
python -c "from main import app"
\`\`\`

### Database Connection Issues

\`\`\`bash
# Test connection
psql -U yago_user -d yago_prod -h localhost

# Check service
sudo systemctl status postgresql
\`\`\`

### High Memory Usage

\`\`\`bash
# Check processes
ps aux | grep gunicorn

# Adjust workers (recommended: 2*CPU+1)
sudo nano /etc/systemd/system/yago-backend.service
# Change --workers value
\`\`\`

### Slow API Responses (Sprint 4)

\`\`\`bash
# Check pagination is working
curl "https://api.yourdomain.com/api/v1/projects?page=1&page_size=20"

# Check database indexes
psql -U yago_user -d yago_prod
\\di

# Analyze slow queries
EXPLAIN ANALYZE SELECT * FROM projects LIMIT 10;
\`\`\`

---

## Post-Deployment Checklist

### Security (Sprint 1)
- [ ] JWT_SECRET_KEY is set and secure
- [ ] CORS_ORIGINS configured correctly
- [ ] Input validation working (test with malicious input)
- [ ] Rate limiting enabled
- [ ] SSL certificate installed

### Performance (Sprint 2)
- [ ] Database indexes verified
- [ ] Pagination working on all list endpoints
- [ ] Caching enabled (check X-Cache headers)
- [ ] Response times < 200ms for most endpoints

### Testing (Sprint 3)
- [ ] Backend tests passing: `pytest`
- [ ] Frontend tests passing: `npm test`
- [ ] Integration tests verified
- [ ] Test coverage > 60%

### API Documentation (Sprint 4)
- [ ] Swagger UI accessible: `/docs`
- [ ] All endpoints documented
- [ ] Examples working

### Monitoring (Sprint 5)
- [ ] Error logging working
- [ ] Analytics dashboard accessible
- [ ] Backup script running
- [ ] Health checks returning 200

---

## Support

- **Issues:** https://github.com/lekesiz/yago/issues
- **Documentation:** View API docs at `https://yourdomain.com/docs`
- **Version:** 8.4.0

---

**Successfully deployed?** Run the test suite to verify:

\`\`\`bash
# Backend tests
cd /path/to/yago/web/backend
pytest -v

# Frontend tests  
cd /path/to/yago/web/frontend
npm test
\`\`\`

🎉 Congratulations! YAGO v8.4 is now running in production with enterprise-grade security, performance, and monitoring!
