#!/bin/bash
# JARVIS Startup Script
# This script starts all JARVIS services using Docker Compose

set -e

echo "🤖 Starting JARVIS Personal AI Assistant..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys:"
    echo "  cp .env.example .env"
    echo ""
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker and try again."
    echo ""
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Create models directory for Whisper if it doesn't exist
mkdir -p models

echo "✅ Pre-flight checks passed"
echo ""

# Pull latest images
echo "📦 Pulling Docker images..."
docker-compose pull

# Build services
echo "🔨 Building JARVIS services..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for database to be ready
echo ""
echo "⏳ Waiting for database to initialize..."
sleep 5

# Check service health
echo ""
echo "🏥 Checking service health..."
docker-compose ps

echo ""
echo "✅ JARVIS is now running!"
echo ""
echo "📊 Dashboard: http://localhost:3000"
echo "🔌 API: http://localhost:5000"
echo "🗄️  Database: localhost:5432"
echo ""
echo "📝 View logs: ./scripts/logs.sh"
echo "🛑 Stop JARVIS: ./scripts/stop.sh"
echo ""
