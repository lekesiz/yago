#!/bin/bash

# YAGO v8.0 - Local Development Starter
# Otomatik olarak backend ve frontend'i başlatır

set -e  # Exit on error

echo "🚀 YAGO v8.0 - Lokal Development Başlatılıyor..."
echo "================================================="

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[→]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Step 1: Check prerequisites
print_step "Adım 1/7: Ön gereksinimleri kontrol ediliyor..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 bulunamadı. Lütfen Python 3.11+ kurun."
    exit 1
fi

if ! command -v node &> /dev/null; then
    print_error "Node.js bulunamadı. Lütfen Node.js 18+ kurun."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
NODE_VERSION=$(node --version | cut -d 'v' -f 2)

print_info "Python $PYTHON_VERSION ✓"
print_info "Node.js $NODE_VERSION ✓"

# Step 2: Create virtual environment
print_step "Adım 2/7: Python virtual environment hazırlanıyor..."

if [ ! -d "venv" ]; then
    print_warning "Virtual environment bulunamadı, oluşturuluyor..."
    python3 -m venv venv
    print_info "Virtual environment oluşturuldu"
else
    print_info "Virtual environment mevcut"
fi

# Step 3: Install Python dependencies
print_step "Adım 3/7: Python bağımlılıkları yükleniyor..."

source venv/bin/activate

if [ -f "requirements.txt" ]; then
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    print_info "Python bağımlılıkları yüklendi"
else
    print_error "requirements.txt bulunamadı!"
    exit 1
fi

# Step 4: Create .env file
print_step "Adım 4/7: Environment variables ayarlanıyor..."

if [ ! -f ".env" ]; then
    print_warning ".env dosyası bulunamadı, oluşturuluyor..."
    cat > .env << 'EOF'
# YAGO Local Development Configuration

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug

# Database (SQLite)
DATABASE_TYPE=sqlite
DATABASE_PATH=./data/yago.db

# Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Frontend
FRONTEND_URL=http://localhost:3000

# JWT Secret (for testing only)
JWT_SECRET=local-development-secret-key-change-in-production

# AI APIs (Optional - for testing)
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_AI_API_KEY=...
EOF
    print_info ".env dosyası oluşturuldu"
else
    print_info ".env dosyası mevcut"
fi

# Step 5: Create necessary directories
print_step "Adım 5/7: Gerekli klasörler oluşturuluyor..."

mkdir -p data
mkdir -p logs
mkdir -p uploads

print_info "Klasörler hazır"

# Step 6: Check ports
print_step "Adım 6/7: Port kullanılabilirliği kontrol ediliyor..."

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Port 8000 kullanımda! Mevcut process kapatılıyor..."
    kill -9 $(lsof -ti:8000) 2>/dev/null || true
    sleep 2
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Port 3000 kullanımda! Mevcut process kapatılıyor..."
    kill -9 $(lsof -ti:3000) 2>/dev/null || true
    sleep 2
fi

print_info "Portlar hazır (8000, 3000)"

# Step 7: Start services
print_step "Adım 7/7: Servisler başlatılıyor..."

# Create log files
touch logs/backend.log
touch logs/frontend.log

# Start backend in background
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🔧 Backend Başlatılıyor...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if backend main file exists
if [ ! -f "yago/web/backend/main.py" ]; then
    print_error "Backend main.py bulunamadı!"
    print_warning "Backend dosyası oluşturuluyor..."

    mkdir -p yago/web/backend

    cat > yago/web/backend/main.py << 'BACKEND_EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="YAGO v8.0 API",
    description="Yet Another Genius Orchestrator",
    version="8.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "YAGO v8.0 API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
BACKEND_EOF

    print_info "Backend main.py oluşturuldu (minimal)"
fi

# Start backend
nohup python -m uvicorn yago.web.backend.main:app --reload --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "Backend başlatılıyor (PID: $BACKEND_PID)..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_info "Backend hazır: http://localhost:8000"
    print_info "API Docs: http://localhost:8000/docs"
else
    print_error "Backend başlatılamadı! Log kontrol et: tail -f logs/backend.log"
    exit 1
fi

# Install frontend dependencies if needed
if [ ! -d "yago/web/frontend/node_modules" ]; then
    print_step "Frontend bağımlılıkları yükleniyor..."
    cd yago/web/frontend
    npm install --silent
    cd "$PROJECT_ROOT"
    print_info "Frontend bağımlılıkları yüklendi"
fi

# Start frontend
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎨 Frontend Başlatılıyor...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd yago/web/frontend

# Set environment variable for backend URL
export REACT_APP_API_URL=http://localhost:8000

nohup npm start > ../../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

echo "Frontend başlatılıyor (PID: $FRONTEND_PID)..."
echo "Tarayıcı otomatik açılacak..."
sleep 10

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    print_info "Frontend hazır: http://localhost:3000"
else
    print_warning "Frontend henüz hazır değil, birkaç saniye daha bekleyin..."
fi

cd "$PROJECT_ROOT"

# Success message
echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║                                                    ║"
echo "║          ✅ YAGO v8.0 BAŞARIYLA BAŞLATILDI!        ║"
echo "║                                                    ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "📊 Servis Bilgileri:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🔧 Backend:"
echo "     URL:      http://localhost:8000"
echo "     Docs:     http://localhost:8000/docs"
echo "     Health:   http://localhost:8000/health"
echo "     PID:      $BACKEND_PID"
echo "     Logs:     tail -f logs/backend.log"
echo ""
echo "  🎨 Frontend:"
echo "     URL:      http://localhost:3000"
echo "     PID:      $FRONTEND_PID"
echo "     Logs:     tail -f logs/frontend.log"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔧 Yararlı Komutlar:"
echo "  • Logları izle:     tail -f logs/backend.log"
echo "  • Backend durdur:   kill $BACKEND_PID"
echo "  • Frontend durdur:  kill $FRONTEND_PID"
echo "  • Tümünü durdur:    ./scripts/stop-local.sh"
echo ""
echo "📚 Dokümantasyon:"
echo "  • Lokal setup:      LOCAL_SETUP.md"
echo "  • Test rehberi:     LOCAL_SETUP.md (Test Senaryoları)"
echo "  • API docs:         http://localhost:8000/docs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 Şimdi Ne Yapmalı?"
echo "  1. Tarayıcıda http://localhost:3000 adresini aç"
echo "  2. LOCAL_SETUP.md'deki test senaryolarını takip et"
echo "  3. Her test sonucunu kaydet"
echo ""
echo "💡 Test yaparken sorun olursa:"
echo "  • Backend logs: tail -f logs/backend.log"
echo "  • Frontend logs: tail -f logs/frontend.log"
echo ""
echo "Başarılar! 🚀"
echo ""

# Save PIDs to file for stop script
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid
