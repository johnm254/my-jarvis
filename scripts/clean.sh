#!/bin/bash
# JARVIS Clean Script
# This script removes all JARVIS containers, volumes, and data

set -e

echo "⚠️  WARNING: This will delete ALL JARVIS data including:"
echo "  - All Docker containers"
echo "  - All Docker volumes (database data)"
echo "  - All logs"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Clean cancelled."
    exit 0
fi

echo ""
echo "🗑️  Cleaning JARVIS..."
echo ""

# Stop and remove containers
echo "Stopping containers..."
docker-compose down

# Remove volumes
echo "Removing volumes..."
docker-compose down -v

# Remove logs
echo "Removing logs..."
rm -rf logs/*

echo ""
echo "✅ JARVIS has been cleaned"
echo ""
echo "💡 To start fresh: ./scripts/start.sh"
echo ""
