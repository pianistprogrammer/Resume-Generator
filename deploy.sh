#!/bin/bash

# JobAlert AI - Docker Deployment Script
# This script sets up and starts the entire application

set -e  # Exit on error

echo "========================================"
echo "JobAlert AI - Docker Deployment"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Check for .env files
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.docker .env
    echo "⚠️  Please edit .env file with your MongoDB credentials"
fi

if [ ! -f "backend/.env" ]; then
    echo "📝 Creating backend/.env file..."
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo "⚠️  Please edit backend/.env file with your API keys and secrets"
    else
        echo "❌ backend/.env.example not found"
        exit 1
    fi
fi

echo ""
echo "🐳 Starting Docker Compose services..."
echo ""

# Start services
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🔧 Initializing database..."
echo ""

# Wait for backend to be ready
max_attempts=30
attempt=0
until docker-compose exec -T backend python -c "from app.database import connect_to_mongo; connect_to_mongo(); print('Connected')" 2>/dev/null; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ Backend failed to start after $max_attempts attempts"
        echo ""
        echo "View logs with: docker-compose logs backend"
        exit 1
    fi
    echo "Waiting for backend to be ready... (attempt $attempt/$max_attempts)"
    sleep 2
done

echo ""
echo "✓ Backend is ready"

# Populate feed sources
echo ""
echo "📰 Populating RSS feed sources..."
docker-compose exec -T backend python scripts/populate_feeds.py

echo ""
echo "========================================"
echo "✅ Deployment Complete!"
echo "========================================"
echo ""
echo "🌐 Services are running:"
echo "   - Frontend:  http://localhost:3000"
echo "   - Backend:   http://localhost:8000"
echo "   - API Docs:  http://localhost:8000/docs"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f [service-name]"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
echo "📖 For more information, see DOCKER_DEPLOYMENT.md"
echo ""
