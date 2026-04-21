# JARVIS Startup Script (PowerShell)
# This script starts all JARVIS services using Docker Compose

$ErrorActionPreference = "Stop"

Write-Host "🤖 Starting JARVIS Personal AI Assistant..." -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and configure your API keys:"
    Write-Host "  Copy-Item .env.example .env"
    Write-Host ""
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Error: Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker and try again."
    Write-Host ""
    exit 1
}

# Create logs directory if it doesn't exist
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Create models directory for Whisper if it doesn't exist
if (-not (Test-Path "models")) {
    New-Item -ItemType Directory -Path "models" | Out-Null
}

Write-Host "✅ Pre-flight checks passed" -ForegroundColor Green
Write-Host ""

# Pull latest images
Write-Host "📦 Pulling Docker images..." -ForegroundColor Yellow
docker-compose pull

# Build services
Write-Host "🔨 Building JARVIS services..." -ForegroundColor Yellow
docker-compose build

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for database to be ready
Write-Host ""
Write-Host "⏳ Waiting for database to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check service health
Write-Host ""
Write-Host "🏥 Checking service health..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "✅ JARVIS is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Dashboard: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔌 API: http://localhost:5000" -ForegroundColor Cyan
Write-Host "🗄️  Database: localhost:5432" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 View logs: .\scripts\logs.ps1" -ForegroundColor Gray
Write-Host "🛑 Stop JARVIS: .\scripts\stop.ps1" -ForegroundColor Gray
Write-Host ""
