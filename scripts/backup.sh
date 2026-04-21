#!/bin/bash
# JARVIS Database Backup Script
# This script creates a backup of the JARVIS database

set -e

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/jarvis_backup_$TIMESTAMP.sql"

echo "💾 Creating JARVIS database backup..."
echo ""

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Get database password from .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-your-super-secret-password}

# Create backup
docker exec jarvis-supabase-db pg_dump -U postgres jarvis > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

echo "✅ Backup created: ${BACKUP_FILE}.gz"
echo ""
echo "📊 Backup size: $(du -h ${BACKUP_FILE}.gz | cut -f1)"
echo ""
echo "💡 To restore: ./scripts/restore.sh ${BACKUP_FILE}.gz"
echo ""
