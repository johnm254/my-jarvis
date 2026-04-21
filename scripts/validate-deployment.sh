#!/bin/bash
# JARVIS Deployment Validation Script
# This script validates the complete deployment setup

set -e

PASSED=0
FAILED=0
WARNINGS=0

echo "🔍 JARVIS Deployment Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Helper functions
pass() {
    echo "  ✅ $1"
    PASSED=$((PASSED + 1))
}

fail() {
    echo "  ❌ $1"
    FAILED=$((FAILED + 1))
}

warn() {
    echo "  ⚠️  $1"
    WARNINGS=$((WARNINGS + 1))
}

info() {
    echo "  ℹ️  $1"
}

# Test 1: Check Docker
echo "1️⃣  Checking Docker..."
if command -v docker &> /dev/null; then
    if docker info > /dev/null 2>&1; then
        pass "Docker is installed and running"
    else
        fail "Docker is installed but not running"
    fi
else
    fail "Docker is not installed"
fi
echo ""

# Test 2: Check Docker Compose
echo "2️⃣  Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    VERSION=$(docker-compose version --short)
    pass "Docker Compose is installed (version $VERSION)"
else
    fail "Docker Compose is not installed"
fi
echo ""

# Test 3: Check Configuration Files
echo "3️⃣  Checking Configuration Files..."

if [ -f "docker-compose.yml" ]; then
    pass "docker-compose.yml exists"
    
    # Validate docker-compose.yml
    if docker-compose config > /dev/null 2>&1; then
        pass "docker-compose.yml is valid"
    else
        fail "docker-compose.yml has syntax errors"
    fi
else
    fail "docker-compose.yml not found"
fi

if [ -f "Dockerfile" ]; then
    pass "Dockerfile exists"
else
    fail "Dockerfile not found"
fi

if [ -f "init-db.sql" ]; then
    pass "init-db.sql exists"
else
    fail "init-db.sql not found"
fi

if [ -f ".env.example" ]; then
    pass ".env.example exists"
else
    fail ".env.example not found"
fi

if [ -f ".env" ]; then
    pass ".env exists"
else
    warn ".env not found (run: cp .env.example .env)"
fi
echo ""

# Test 4: Check Environment Variables
echo "4️⃣  Checking Environment Variables..."
if [ -f ".env" ]; then
    # Check required variables
    REQUIRED_VARS=("LLM_API_KEY" "SUPABASE_URL" "SUPABASE_KEY" "JWT_SECRET")
    
    for VAR in "${REQUIRED_VARS[@]}"; do
        if grep -q "^${VAR}=..*" .env; then
            pass "$VAR is configured"
        else
            warn "$VAR is not configured in .env"
        fi
    done
    
    # Check optional variables
    OPTIONAL_VARS=("TTS_API_KEY" "PORCUPINE_ACCESS_KEY" "BRAVE_API_KEY" "WEATHER_API_KEY" "GITHUB_TOKEN")
    
    for VAR in "${OPTIONAL_VARS[@]}"; do
        if grep -q "^${VAR}=..*" .env; then
            info "$VAR is configured (optional)"
        fi
    done
else
    fail "Cannot check environment variables (.env not found)"
fi
echo ""

# Test 5: Check Scripts
echo "5️⃣  Checking Deployment Scripts..."
SCRIPTS=("start.sh" "stop.sh" "logs.sh" "status.sh" "backup.sh" "restore.sh" "clean.sh" "dev.sh" "db-shell.sh" "setup.sh" "health-check.sh" "migrate.sh")

for SCRIPT in "${SCRIPTS[@]}"; do
    if [ -f "scripts/$SCRIPT" ]; then
        if [ -x "scripts/$SCRIPT" ]; then
            pass "scripts/$SCRIPT exists and is executable"
        else
            warn "scripts/$SCRIPT exists but is not executable (run: chmod +x scripts/*.sh)"
        fi
    else
        fail "scripts/$SCRIPT not found"
    fi
done
echo ""

# Test 6: Check Directories
echo "6️⃣  Checking Required Directories..."
DIRS=("logs" "models" "backups" "migrations")

for DIR in "${DIRS[@]}"; do
    if [ -d "$DIR" ]; then
        pass "$DIR/ directory exists"
    else
        warn "$DIR/ directory not found (will be created on startup)"
    fi
done
echo ""

# Test 7: Check Documentation
echo "7️⃣  Checking Documentation..."
DOCS=("README.md" "DEPLOYMENT.md" "QUICK_START.md" "DEPLOYMENT_TEST.md" "scripts/README.md")

for DOC in "${DOCS[@]}"; do
    if [ -f "$DOC" ]; then
        pass "$DOC exists"
    else
        warn "$DOC not found"
    fi
done
echo ""

# Test 8: Check Makefile
echo "8️⃣  Checking Makefile..."
if [ -f "Makefile" ]; then
    pass "Makefile exists"
    
    # Check if make is installed
    if command -v make &> /dev/null; then
        pass "make command is available"
    else
        warn "make command not found (Makefile won't work)"
    fi
else
    warn "Makefile not found"
fi
echo ""

# Test 9: Check Running Services
echo "9️⃣  Checking Running Services..."
if docker-compose ps > /dev/null 2>&1; then
    RUNNING=$(docker-compose ps --services --filter "status=running" | wc -l)
    TOTAL=$(docker-compose ps --services | wc -l)
    
    if [ "$RUNNING" -eq "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
        pass "All services are running ($RUNNING/$TOTAL)"
    elif [ "$RUNNING" -gt 0 ]; then
        warn "Some services are running ($RUNNING/$TOTAL)"
    else
        info "No services are currently running (run: ./scripts/start.sh)"
    fi
else
    info "Cannot check services (docker-compose not available)"
fi
echo ""

# Test 10: Check Database (if running)
echo "🔟 Checking Database..."
if docker ps | grep -q "jarvis-supabase-db"; then
    if docker exec jarvis-supabase-db pg_isready -U postgres > /dev/null 2>&1; then
        pass "Database is running and accepting connections"
        
        # Check tables
        TABLE_COUNT=$(docker exec jarvis-supabase-db psql -U postgres jarvis -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
        if [ "$TABLE_COUNT" -gt 0 ]; then
            pass "Database schema is initialized ($TABLE_COUNT tables)"
        else
            warn "Database schema not initialized"
        fi
    else
        fail "Database is running but not accepting connections"
    fi
else
    info "Database is not running"
fi
echo ""

# Test 11: Check Disk Space
echo "1️⃣1️⃣  Checking System Resources..."
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    pass "Disk space is adequate ($DISK_USAGE% used)"
elif [ "$DISK_USAGE" -lt 90 ]; then
    warn "Disk space is getting low ($DISK_USAGE% used)"
else
    fail "Disk space is critically low ($DISK_USAGE% used)"
fi

# Check memory (if available)
if command -v free &> /dev/null; then
    TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_MEM" -ge 4 ]; then
        pass "Memory is adequate (${TOTAL_MEM}GB total)"
    else
        warn "Memory may be insufficient (${TOTAL_MEM}GB total, 4GB recommended)"
    fi
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Validation Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ✅ Passed:   $PASSED"
echo "  ⚠️  Warnings: $WARNINGS"
echo "  ❌ Failed:   $FAILED"
echo ""

if [ "$FAILED" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo "🎉 Perfect! Your deployment is ready!"
    echo ""
    echo "Next steps:"
    echo "  1. Start JARVIS: ./scripts/start.sh"
    echo "  2. Access dashboard: http://localhost:3000"
    echo ""
    exit 0
elif [ "$FAILED" -eq 0 ]; then
    echo "✅ Good! Your deployment is mostly ready."
    echo ""
    echo "Please address the warnings above for optimal operation."
    echo ""
    echo "To start JARVIS: ./scripts/start.sh"
    echo ""
    exit 0
else
    echo "❌ Issues found! Please fix the failed checks above."
    echo ""
    echo "Common fixes:"
    echo "  - Install Docker: https://docs.docker.com/get-docker/"
    echo "  - Create .env: cp .env.example .env"
    echo "  - Make scripts executable: chmod +x scripts/*.sh"
    echo ""
    exit 1
fi
