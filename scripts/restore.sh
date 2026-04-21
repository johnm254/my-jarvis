#!/bin/bash
# JARVIS Database Restore Script
# This script restores a JARVIS database backup

set -e

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ Error: No backup file specified!"
    echo ""
    echo "Usage: ./scripts/restore.sh <backup_file>"
    echo ""
    echo "Available backups:"
    ls -lh backups/ 2>/dev/null || echo "  No backups found"
    echo ""
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  WARNING: This will replace the current database!"
echo "Backup file: $BACKUP_FILE"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo ""
echo "🔄 Restoring database from backup..."
echo ""

# Get database password from .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-your-super-secret-password}

# Decompress if needed
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo "📦 Decompressing backup..."
    gunzip -c "$BACKUP_FILE" | docker exec -i jarvis-supabase-db psql -U postgres jarvis
else
    cat "$BACKUP_FILE" | docker exec -i jarvis-supabase-db psql -U postgres jarvis
fi

echo ""
echo "✅ Database restored successfully!"
echo ""
