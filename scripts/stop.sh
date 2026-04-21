#!/bin/bash
# JARVIS Stop Script
# This script stops all JARVIS services

set -e

echo "🛑 Stopping JARVIS Personal AI Assistant..."
echo ""

# Stop all services
docker-compose down

echo ""
echo "✅ JARVIS has been stopped"
echo ""
echo "💡 To start again: ./scripts/start.sh"
echo "🗑️  To remove all data: ./scripts/clean.sh"
echo ""
