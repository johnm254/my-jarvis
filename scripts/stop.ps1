# JARVIS Stop Script (PowerShell)
# This script stops all JARVIS services

$ErrorActionPreference = "Stop"

Write-Host "🛑 Stopping JARVIS Personal AI Assistant..." -ForegroundColor Yellow
Write-Host ""

# Stop all services
docker-compose down

Write-Host ""
Write-Host "✅ JARVIS has been stopped" -ForegroundColor Green
Write-Host ""
Write-Host "💡 To start again: .\scripts\start.ps1" -ForegroundColor Gray
Write-Host "🗑️  To remove all data: .\scripts\clean.ps1" -ForegroundColor Gray
Write-Host ""
