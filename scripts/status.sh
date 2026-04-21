#!/bin/bash
# JARVIS Status Script
# This script shows the status of all JARVIS services

echo "🤖 JARVIS System Status"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    exit 1
fi

# Show container status
echo "📦 Services:"
docker-compose ps

echo ""
echo "💾 Disk Usage:"
docker system df

echo ""
echo "🔌 Network:"
docker network inspect jarvis-network --format '{{.Name}}: {{len .Containers}} containers connected' 2>/dev/null || echo "Network not found"

echo ""
echo "📊 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker-compose ps -q 2>/dev/null) 2>/dev/null || echo "No containers running"

echo ""
