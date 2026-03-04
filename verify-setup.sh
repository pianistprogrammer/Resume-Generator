#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 JobAlert AI - Setup Verification Script"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Backend checks
echo "📦 Checking Backend Setup..."
echo ""

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python installed: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python 3 not found${NC}"
fi

# Check uv
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    echo -e "${GREEN}✅ uv installed: $UV_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  uv not installed (recommended for faster dependency management)${NC}"
    echo "   Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# Check backend files
if [ -f "backend/main.py" ]; then
    echo -e "${GREEN}✅ main.py exists at backend/main.py${NC}"
else
    echo -e "${RED}❌ main.py not found at backend/main.py${NC}"
fi

if [ -f "backend/.env" ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"

    # Check for SECRET_KEY
    if grep -q "SECRET_KEY=gtk" backend/.env; then
        echo -e "${GREEN}✅ SECRET_KEY is configured${NC}"
    else
        echo -e "${YELLOW}⚠️  SECRET_KEY not configured properly${NC}"
    fi
else
    echo -e "${RED}❌ .env file not found in backend/${NC}"
fi

if [ -f "backend/pyproject.toml" ]; then
    echo -e "${GREEN}✅ pyproject.toml exists (uv config)${NC}"
else
    echo -e "${YELLOW}⚠️  pyproject.toml not found${NC}"
fi

# Check if MongoDB is running
if command -v mongosh &> /dev/null || command -v mongo &> /dev/null; then
    if mongosh --eval "db.version()" &> /dev/null || mongo --eval "db.version()" &> /dev/null; then
        echo -e "${GREEN}✅ MongoDB is running${NC}"
    else
        echo -e "${YELLOW}⚠️  MongoDB installed but not running${NC}"
        echo "   Start: brew services start mongodb-community"
    fi
else
    echo -e "${YELLOW}⚠️  MongoDB not detected${NC}"
    echo "   Install: brew install mongodb-community"
fi

# Check if Redis is running
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✅ Redis is running${NC}"
    else
        echo -e "${YELLOW}⚠️  Redis installed but not running${NC}"
        echo "   Start: brew services start redis"
    fi
else
    echo -e "${YELLOW}⚠️  Redis not detected${NC}"
    echo "   Install: brew install redis"
fi

echo ""
echo "🎨 Checking Frontend Setup..."
echo ""

# Check Node version
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2)
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)

    if [ "$NODE_MAJOR" -ge 22 ]; then
        echo -e "${GREEN}✅ Node.js installed: v$NODE_VERSION${NC}"
    else
        echo -e "${YELLOW}⚠️  Node.js version $NODE_VERSION (need 22+)${NC}"
        echo "   Install Node 22: nvm install 22 && nvm use 22"
    fi
else
    echo -e "${RED}❌ Node.js not found${NC}"
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✅ npm installed: $NPM_VERSION${NC}"
else
    echo -e "${RED}❌ npm not found${NC}"
fi

# Check nvm
if command -v nvm &> /dev/null || [ -s "$HOME/.nvm/nvm.sh" ]; then
    echo -e "${GREEN}✅ nvm installed${NC}"
else
    echo -e "${YELLOW}⚠️  nvm not installed (recommended for Node version management)${NC}"
    echo "   Install: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
fi

# Check frontend files
if [ -f "frontend/.nvmrc" ]; then
    echo -e "${GREEN}✅ .nvmrc file exists (specifies Node 22)${NC}"
else
    echo -e "${YELLOW}⚠️  .nvmrc not found${NC}"
fi

if [ -f "frontend/package.json" ]; then
    echo -e "${GREEN}✅ package.json exists${NC}"
else
    echo -e "${RED}❌ package.json not found${NC}"
fi

# Check if node_modules exists
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✅ node_modules installed${NC}"
else
    echo -e "${YELLOW}⚠️  node_modules not found${NC}"
    echo "   Install: cd frontend && npm install"
fi

echo ""
echo "🐳 Checking Docker (Optional)..."
echo ""

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    echo -e "${GREEN}✅ Docker installed: $DOCKER_VERSION${NC}"

    # Check if Docker is running
    if docker info &> /dev/null; then
        echo -e "${GREEN}✅ Docker daemon is running${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker installed but daemon not running${NC}"
        echo "   Start Docker Desktop"
    fi
else
    echo -e "${YELLOW}⚠️  Docker not installed (optional)${NC}"
fi

# Check docker-compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f4 | cut -d',' -f1)
    echo -e "${GREEN}✅ docker-compose installed: $COMPOSE_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  docker-compose not installed (optional)${NC}"
fi

echo ""
echo "📋 Summary & Next Steps"
echo "=========================================="
echo ""

# Determine what to suggest
MISSING_CRITICAL=false

if ! command -v python3 &> /dev/null || ! [ -f "backend/main.py" ] || ! [ -f "backend/.env" ]; then
    MISSING_CRITICAL=true
fi

if ! command -v node &> /dev/null || ! [ -f "frontend/package.json" ]; then
    MISSING_CRITICAL=true
fi

if [ "$MISSING_CRITICAL" = true ]; then
    echo -e "${RED}❌ Critical components missing${NC}"
    echo ""
    echo "Please fix the issues above before starting the application."
else
    echo -e "${GREEN}✅ All critical components present!${NC}"
    echo ""
    echo "🚀 Ready to start the application:"
    echo ""
    echo "Option 1: Docker Compose (Recommended)"
    echo "  cd backend && docker-compose up -d"
    echo ""
    echo "Option 2: Local Development"
    echo "  Terminal 1: cd backend && uvicorn main:app --reload"
    echo "  Terminal 2: cd backend && celery -A app.workers.celery_worker worker --loglevel=info"
    echo "  Terminal 3: cd frontend && npm run dev"
    echo ""
    echo "Then visit:"
    echo "  Frontend: http://localhost:3000"
    echo "  API Docs: http://localhost:8000/docs"
fi

echo ""
echo "📚 For more help, see:"
echo "  QUICKSTART.md - Quick setup guide"
echo "  REFACTORING_SUMMARY.md - Recent changes"
echo "  backend/README.md - Backend details"
echo "  frontend/README.md - Frontend details"
echo ""
