#!/bin/bash
# JARVIS Logs Script
# This script displays logs from JARVIS services

# Default to showing all services
SERVICE=${1:-}

if [ -z "$SERVICE" ]; then
    echo "📝 Showing logs from all JARVIS services..."
    echo "   (Press Ctrl+C to exit)"
    echo ""
    docker-compose logs -f
else
    echo "📝 Showing logs from $SERVICE..."
    echo "   (Press Ctrl+C to exit)"
    echo ""
    docker-compose logs -f "$SERVICE"
fi
