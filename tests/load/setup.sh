#!/bin/bash

################################################################################
# YAGO v8.1 Load Testing - Quick Setup Script
################################################################################

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}YAGO Load Testing Setup${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 is not installed!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found:${NC} $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Verify installation
echo ""
echo "Verifying installation..."
locust --version
echo -e "${GREEN}✓ Locust installed successfully${NC}"

# Create results directory
mkdir -p results
echo -e "${GREEN}✓ Results directory created${NC}"

# Make scripts executable
chmod +x run_tests.sh
echo -e "${GREEN}✓ Scripts made executable${NC}"

echo ""
echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Start the YAGO backend:"
echo "     cd /Users/mikail/Desktop/YAGO/yago/web/backend"
echo "     python api.py"
echo ""
echo "  2. Run a quick test:"
echo "     ./run_tests.sh quick http://localhost:8000"
echo ""
echo "  3. Or launch Locust web UI:"
echo "     locust -f locustfile.py --host=http://localhost:8000"
echo "     Then open: http://localhost:8089"
echo ""
echo "For more information, see README.md"
echo ""
