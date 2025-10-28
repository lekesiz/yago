# 🚀 YAGO v8.0 - Deployment Guide

Comprehensive deployment guide for YAGO v8.0 with two recommended options:
1. **Google Cloud Run + Firestore** (Production-ready, serverless)
2. **Vercel + Railway + Neon** (Quick start, MVP)

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Option 1: Google Cloud Run + Firestore](#option-1-google-cloud-run--firestore)
- [Option 2: Vercel + Railway + Neon](#option-2-vercel--railway--neon)
- [Environment Variables](#environment-variables)
- [Post-Deployment](#post-deployment)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### General Requirements

```bash
# Node.js 18+
node --version  # v18.0.0+

# Python 3.11+
python3 --version  # 3.11.0+

# Git
git --version
```

### API Keys (Optional, but recommended)

```bash
# AI Model APIs (at least one recommended)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_AI_API_KEY="..."

# Email (for notifications)
export SENDGRID_API_KEY="SG..."
```

---

## Option 1: Google Cloud Run + Firestore

**Best for**: Production deployments, enterprise use, high scalability

**Cost**: ~$60/month for moderate usage

**Setup time**: ~50 minutes

### 1.1 Install Google Cloud SDK

```bash
# macOS
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash

# Windows
# Download from: https://cloud.google.com/sdk/docs/install

# Initialize
gcloud init
```

### 1.2 Create GCP Project

```bash
# Create project
gcloud projects create yago-production --name="YAGO Production"

# Set as default
gcloud config set project yago-production

# Enable billing (required)
# Visit: https://console.cloud.google.com/billing
```

### 1.3 Set Environment Variables

```bash
export GCP_PROJECT_ID="yago-production"
export GCP_REGION="europe-west1"  # or us-central1, asia-east1
```

### 1.4 Deploy with One Command

```bash
cd /path/to/YAGO
./deployment/deploy-gcp.sh
```

**What it does**:
1. ✓ Enables required Google Cloud APIs
2. ✓ Creates Firestore database
3. ✓ Deploys security rules and indexes
4. ✓ Builds Docker containers
5. ✓ Deploys backend to Cloud Run
6. ✓ Deploys frontend to Cloud Run
7. ✓ Configures environment variables

### 1.5 Verify Deployment

```bash
# Check backend health
curl https://yago-backend-xxxx-ew.a.run.app/health

# Check frontend
curl https://yago-frontend-xxxx-ew.a.run.app/

# View logs
gcloud run logs read --service=yago-backend --limit=50
```

### 1.6 Custom Domain (Optional)

```bash
# Map custom domain
gcloud run domain-mappings create \
    --service=yago-frontend \
    --domain=app.yourdomain.com \
    --region=europe-west1

# Add DNS record (shown in output)
```

---

## Option 2: Vercel + Railway + Neon

**Best for**: Quick start, MVP, testing

**Cost**: $0-5/month (free tier available)

**Setup time**: ~20 minutes

### 2.1 Install CLI Tools

```bash
# Vercel CLI
npm i -g vercel

# Railway CLI
npm i -g @railway/cli
```

### 2.2 Create Neon Database

1. Visit [console.neon.tech](https://console.neon.tech)
2. Create new project: "yago-production"
3. Copy connection string:
   ```
   postgresql://user:pass@ep-xxx.region.aws.neon.tech/yago
   ```
4. Save as `NEON_DATABASE_URL`

### 2.3 Deploy Backend to Railway

**Option A: Automated (CLI)**

```bash
cd /path/to/YAGO
railway login
railway init
railway up
```

**Option B: Manual (Dashboard)**

1. Visit [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select `lekesiz/yago`
4. Configuration:
   - **Dockerfile Path**: `deployment/Dockerfile.backend`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Memory**: 2GB
   - **CPU**: 2 cores

5. Add environment variables:
   ```
   NEON_DATABASE_URL=postgresql://...
   ENVIRONMENT=production
   LOG_LEVEL=info
   ```

6. Generate domain → Copy backend URL

### 2.4 Deploy Frontend to Vercel

```bash
cd yago/web/frontend

# Link to Vercel
vercel

# Set environment variable
vercel env add REACT_APP_API_URL production
# Paste Railway backend URL

# Deploy production
vercel --prod
```

**Or via Dashboard**:

1. Visit [vercel.com](https://vercel.com)
2. Import `lekesiz/yago`
3. Framework Preset: **Create React App**
4. Root Directory: `yago/web/frontend`
5. Environment Variables:
   ```
   REACT_APP_API_URL=https://yago-backend.railway.app
   ```
6. Deploy

---

## Environment Variables

### Backend (Required)

```bash
# Database
NEON_DATABASE_URL=postgresql://...       # Neon/PostgreSQL connection

# Environment
ENVIRONMENT=production
LOG_LEVEL=info
PORT=8080                                # Auto-set by Cloud Run/Railway
```

### Backend (Optional - AI Models)

```bash
# OpenAI (GPT models)
OPENAI_API_KEY=sk-...

# Anthropic (Claude models)
ANTHROPIC_API_KEY=sk-ant-...

# Google AI (Gemini models)
GOOGLE_AI_API_KEY=...

# Local models (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
```

### Frontend (Required)

```bash
REACT_APP_API_URL=https://your-backend-url
REACT_APP_ENVIRONMENT=production
```

---

## Post-Deployment

### 1. Verify All Endpoints

```bash
# Backend health
curl https://your-backend/health

# Test API
curl https://your-backend/api/v1/models/list

# Frontend
curl https://your-frontend/
```

### 2. Create Admin User

```bash
curl -X POST https://your-backend/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourdomain.com",
    "password": "secure_password_123",
    "role": "ADMIN"
  }'
```

### 3. Test Core Features

```bash
# Create a workflow
curl -X POST https://your-backend/api/v1/workflows/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Test Workflow",
    "model_id": "gpt-4"
  }'

# Check analytics
curl https://your-backend/api/v1/analytics/summary \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Monitoring

### Google Cloud Run

```bash
# View metrics
gcloud run services describe yago-backend \
  --region=europe-west1 \
  --format="value(status.url)"

# Real-time logs
gcloud run logs tail --service=yago-backend

# Check quotas
gcloud compute project-info describe --project=yago-production
```

### Railway

```bash
# View logs
railway logs

# Check metrics
railway status
```

### Vercel

```bash
# View deployment logs
vercel logs

# Check analytics
vercel analytics
```

---

## Troubleshooting

### Issue: Backend returns 500 errors

**Solution**: Check logs and environment variables

```bash
# Google Cloud Run
gcloud run logs read --service=yago-backend --limit=100

# Railway
railway logs --tail=100

# Common fixes
- Verify NEON_DATABASE_URL is correct
- Check API keys are valid
- Ensure PORT is set correctly
```

### Issue: Frontend can't reach backend

**Solution**: CORS or environment variable issue

```bash
# Verify REACT_APP_API_URL
vercel env ls

# Check CORS settings in backend
# File: yago/web/backend/main.py
# Ensure frontend URL is in allowed_origins
```

### Issue: Database connection fails

**Solution**: Check Neon/Firestore configuration

```bash
# Test connection string
psql "$NEON_DATABASE_URL"

# Or for Firestore
gcloud firestore databases describe
```

### Issue: Cold start latency

**Solutions**:

1. **Google Cloud Run**: Set min instances
   ```bash
   gcloud run services update yago-backend \
       --min-instances=1 \
       --region=europe-west1
   ```

2. **Railway**: Enable always-on
   ```bash
   # In Railway dashboard → Settings → Enable "Always On"
   ```

---

## Performance Optimization

### 1. Enable CDN (Vercel)

Automatically enabled for static assets. Verify:

```bash
curl -I https://your-frontend/static/js/main.js
# Should show: x-vercel-cache: HIT
```

### 2. Database Indexing

Firestore indexes are auto-deployed. For Neon:

```sql
-- Create indexes for common queries
CREATE INDEX idx_workflows_user_created ON workflows(user_id, created_at DESC);
CREATE INDEX idx_sessions_user ON sessions(user_id);
```

### 3. Enable Compression

Already configured in:
- `deployment/nginx.conf` (frontend)
- FastAPI automatic gzip (backend)

---

## Security Checklist

- [ ] All API keys stored in environment variables (not in code)
- [ ] Firestore security rules deployed
- [ ] HTTPS enabled (automatic on all platforms)
- [ ] CORS configured correctly
- [ ] Rate limiting enabled (Cloud Run/Railway)
- [ ] Regular security updates scheduled

---

## Cost Monitoring

### Google Cloud Run

```bash
# View current costs
gcloud billing accounts list
gcloud billing projects describe yago-production

# Set budget alerts
# Visit: https://console.cloud.google.com/billing/budgets
```

### Railway

- Free tier: $5 credit/month
- Check usage: [railway.app/account](https://railway.app/account)

### Neon

- Free tier: 0.5GB storage, 100 hours compute
- Check usage: [console.neon.tech](https://console.neon.tech)

---

## Scaling

### Horizontal Scaling

**Google Cloud Run** (automatic):
```bash
gcloud run services update yago-backend \
    --min-instances=1 \
    --max-instances=100 \
    --region=europe-west1
```

**Railway** (automatic):
- Configure in `deployment/railway.toml`
- Auto-scales between 0-3 instances

### Vertical Scaling

**Increase resources**:

```bash
# Cloud Run
gcloud run services update yago-backend \
    --memory=4Gi \
    --cpu=4

# Railway
# Update in dashboard → Settings → Resources
```

---

## Backup and Recovery

### Database Backups

**Firestore** (automatic):
- Point-in-time recovery (PITR) enabled by default
- 7-day retention

**Neon** (automatic):
- Daily backups
- 7-day retention on free tier
- Point-in-time recovery on paid plans

### Manual Backup

```bash
# Firestore export
gcloud firestore export gs://yago-backups/$(date +%Y%m%d)

# Neon backup
pg_dump "$NEON_DATABASE_URL" > backup_$(date +%Y%m%d).sql
```

---

## Support

- **Documentation**: [github.com/lekesiz/yago](https://github.com/lekesiz/yago)
- **Issues**: [github.com/lekesiz/yago/issues](https://github.com/lekesiz/yago/issues)
- **Email**: support@yago.dev

---

## Quick Reference

| Platform | Service | URL | CLI Command |
|----------|---------|-----|-------------|
| Google Cloud | Console | https://console.cloud.google.com | `gcloud` |
| Railway | Dashboard | https://railway.app | `railway` |
| Vercel | Dashboard | https://vercel.com | `vercel` |
| Neon | Console | https://console.neon.tech | - |

---

**Last Updated**: 2025-01-XX
**Version**: 8.0
**Author**: YAGO Team
