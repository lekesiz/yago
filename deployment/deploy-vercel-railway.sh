#!/bin/bash

# YAGO v8.0 - Vercel + Railway + Neon Deployment Script
# Quick deployment for MVP/testing

set -e

echo "🚀 YAGO v8.0 - Vercel + Railway + Neon Deployment"
echo "=================================================="

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Check prerequisites
print_info "Step 1: Checking prerequisites..."

if ! command -v vercel &> /dev/null; then
    print_error "Vercel CLI not found. Install it: npm i -g vercel"
    exit 1
fi

if ! command -v railway &> /dev/null; then
    print_warning "Railway CLI not found. Install it: npm i -g @railway/cli"
    print_warning "Alternatively, deploy via Railway dashboard"
fi

print_info "✓ Prerequisites checked"

# Step 2: Create Neon database
print_info "Step 2: Neon Database Setup"
echo ""
echo "Please create a Neon database manually:"
echo "   1. Visit https://console.neon.tech"
echo "   2. Create new project: 'yago-production'"
echo "   3. Copy the connection string"
echo "   4. Save it as: NEON_DATABASE_URL"
echo ""
read -p "Press ENTER when database is ready..."

# Step 3: Deploy backend to Railway
print_info "Step 3: Deploying backend to Railway..."

if command -v railway &> /dev/null; then
    cd /Users/mikail/Desktop/YAGO
    railway login
    railway init
    railway up

    # Get Railway URL
    RAILWAY_URL=$(railway domain)
    print_info "✓ Backend deployed to Railway: $RAILWAY_URL"
else
    print_warning "Please deploy backend manually:"
    echo "   1. Visit https://railway.app"
    echo "   2. Connect GitHub repository"
    echo "   3. Select deployment/Dockerfile.backend"
    echo "   4. Add environment variables"
    echo ""
    read -p "Enter Railway backend URL: " RAILWAY_URL
fi

# Step 4: Deploy frontend to Vercel
print_info "Step 4: Deploying frontend to Vercel..."

cd /Users/mikail/Desktop/YAGO/yago/web/frontend

# Set environment variable
vercel env add REACT_APP_API_URL production <<< "$RAILWAY_URL"

# Deploy
vercel --prod

VERCEL_URL=$(vercel inspect --token=$VERCEL_TOKEN | grep "URL:" | awk '{print $2}')

print_info "✓ Frontend deployed to Vercel"

# Success message
echo ""
echo "=========================================="
echo -e "${GREEN}✓ DEPLOYMENT SUCCESSFUL!${NC}"
echo "=========================================="
echo ""
echo "📊 Service URLs:"
echo "   Frontend (Vercel):  $VERCEL_URL"
echo "   Backend (Railway):  $RAILWAY_URL"
echo "   Database (Neon):    Neon Console"
echo ""
echo "🔧 Environment Variables to Set:"
echo ""
echo "Railway (Backend):"
echo "   - NEON_DATABASE_URL=<your-neon-connection-string>"
echo "   - OPENAI_API_KEY=<optional>"
echo "   - ANTHROPIC_API_KEY=<optional>"
echo "   - GOOGLE_AI_API_KEY=<optional>"
echo ""
echo "Vercel (Frontend):"
echo "   - REACT_APP_API_URL=$RAILWAY_URL (already set)"
echo ""
echo "📚 Documentation: https://github.com/lekesiz/yago"
echo "=========================================="
