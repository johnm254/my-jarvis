#!/bin/bash
# JARVIS Development Mode Script
# This script starts JARVIS in development mode with hot-reload

set -e

echo "🔧 Starting JARVIS in development mode..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys:"
    echo "  cp .env.example .env"
    echo ""
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Create models directory for Whisper if it doesn't exist
mkdir -p models

echo "✅ Pre-flight checks passed"
echo ""

# Start services with logs attached
echo "🚀 Starting services in development mode..."
echo "   (Press Ctrl+C to stop)"
echo ""

docker-compose up --build
