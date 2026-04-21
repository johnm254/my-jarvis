#!/bin/bash
# JARVIS Health Check Script
# This script performs comprehensive health checks on all JARVIS services

set -e

echo "🏥 JARVIS Health Check"
echo ""

HEALTHY=true

# Check Docker
echo "🐳 Checking Docker..."
if docker info > /dev/null 2>&1; then
    echo "  ✅ Docker is running"
else
    echo "  ❌ Docker is not running"
    HEALTHY=false
fi
echo ""

# Check if services are running
echo "📦 Checking Services..."

check_service() {
    SERVICE=$1
    if docker-compose ps | grep -q "$SERVICE.*Up"; then
        echo "  ✅ $SERVICE is running"
        return 0
    else
        echo "  ❌ $SERVICE is not running"
        HEALTHY=false
        return 1
    fi
}

check_service "jarvis-supabase-db"
check_service "jarvis-brain"
check_service "jarvis-dashboard-api"
check_service "jarvis-dashboard-frontend"

echo ""

# Check database connectivity
echo "🗄️  Checking Database..."
if docker exec jarvis-supabase-db pg_isready -U postgres > /dev/null 2>&1; then
    echo "  ✅ Database is accepting connections"
    
    # Check if tables exist
    TABLE_COUNT=$(docker exec jarvis-supabase-db psql -U postgres jarvis -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
    if [ "$TABLE_COUNT" -gt 0 ]; then
        echo "  ✅ Database schema initialized ($TABLE_COUNT tables)"
    else
        echo "  ⚠️  Database schema not initialized"
        HEALTHY=false
    fi
else
    echo "  ❌ Database is not accepting connections"
    HEALTHY=false
fi
echo ""

# Check API endpoint
echo "🔌 Checking API..."
if curl -f -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "  ✅ API is responding"
else
    echo "  ⚠️  API is not responding (may still be starting up)"
fi
echo ""

# Check Dashboard
echo "🌐 Checking Dashboard..."
if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
    echo "  ✅ Dashboard is accessible"
else
    echo "  ⚠️  Dashboard is not accessible (may still be starting up)"
fi
echo ""

# Check disk space
echo "💾 Checking Disk Space..."
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 90 ]; then
    echo "  ✅ Disk space is adequate ($DISK_USAGE% used)"
else
    echo "  ⚠️  Disk space is running low ($DISK_USAGE% used)"
fi
echo ""

# Check memory
echo "🧠 Checking Memory..."
if command -v free &> /dev/null; then
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
    if [ "$MEM_USAGE" -lt 90 ]; then
        echo "  ✅ Memory usage is normal ($MEM_USAGE% used)"
    else
        echo "  ⚠️  Memory usage is high ($MEM_USAGE% used)"
    fi
else
    echo "  ℹ️  Memory check not available on this system"
fi
echo ""

# Check logs for errors
echo "📝 Checking Recent Errors..."
ERROR_COUNT=$(docker-compose logs --tail=100 2>&1 | grep -i "error" | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo "  ✅ No recent errors in logs"
else
    echo "  ⚠️  Found $ERROR_COUNT error messages in recent logs"
    echo "     Run './scripts/logs.sh' to view details"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$HEALTHY" = true ]; then
    echo "✅ Overall Status: HEALTHY"
    echo ""
    echo "JARVIS is running normally!"
    exit 0
else
    echo "⚠️  Overall Status: UNHEALTHY"
    echo ""
    echo "Some services are not running properly."
    echo "Run './scripts/logs.sh' to investigate issues."
    exit 1
fi
