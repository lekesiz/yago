#!/bin/bash

# YAGO v8.0 - Local Development Stopper
# Çalışan servisleri güvenle durdurur

echo "🛑 YAGO v8.0 - Servisler Durduruluyor..."
echo "========================================"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Stop backend
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID"
        print_info "Backend durduruldu (PID: $BACKEND_PID)"
    else
        print_error "Backend zaten çalışmıyor"
    fi
    rm .backend.pid
else
    # Try to find and kill by port
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        kill -9 $(lsof -ti:8000) 2>/dev/null
        print_info "Backend (port 8000) durduruldu"
    fi
fi

# Stop frontend
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID"
        print_info "Frontend durduruldu (PID: $FRONTEND_PID)"
    else
        print_error "Frontend zaten çalışmıyor"
    fi
    rm .frontend.pid
else
    # Try to find and kill by port
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        kill -9 $(lsof -ti:3000) 2>/dev/null
        print_info "Frontend (port 3000) durduruldu"
    fi
fi

echo ""
echo "✅ Tüm servisler durduruldu!"
echo ""
echo "Tekrar başlatmak için: ./scripts/start-local.sh"
echo ""
