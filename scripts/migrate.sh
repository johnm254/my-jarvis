#!/bin/bash
# JARVIS Database Migration Script
# This script applies database migrations

set -e

MIGRATIONS_DIR="migrations"

echo "🔄 JARVIS Database Migration"
echo ""

# Check if migrations directory exists
if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo "❌ Error: Migrations directory not found: $MIGRATIONS_DIR"
    exit 1
fi

# Check if database is running
if ! docker exec jarvis-supabase-db pg_isready -U postgres > /dev/null 2>&1; then
    echo "❌ Error: Database is not running"
    echo "Please start JARVIS first: ./scripts/start.sh"
    exit 1
fi

# Create migrations tracking table if it doesn't exist
echo "📋 Checking migrations tracking table..."
docker exec jarvis-supabase-db psql -U postgres jarvis -c "
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    migration_file VARCHAR(255) UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT NOW()
);" > /dev/null

echo "✅ Migrations tracking table ready"
echo ""

# Get list of applied migrations
APPLIED_MIGRATIONS=$(docker exec jarvis-supabase-db psql -U postgres jarvis -t -c "SELECT migration_file FROM schema_migrations ORDER BY id;" | tr -d ' ')

# Find migration files
MIGRATION_FILES=$(ls -1 "$MIGRATIONS_DIR"/*.sql 2>/dev/null | sort)

if [ -z "$MIGRATION_FILES" ]; then
    echo "ℹ️  No migration files found in $MIGRATIONS_DIR"
    exit 0
fi

echo "📁 Found migration files:"
echo "$MIGRATION_FILES" | sed 's/^/  - /'
echo ""

# Apply migrations
APPLIED_COUNT=0
SKIPPED_COUNT=0

for MIGRATION_FILE in $MIGRATION_FILES; do
    MIGRATION_NAME=$(basename "$MIGRATION_FILE")
    
    # Check if migration was already applied
    if echo "$APPLIED_MIGRATIONS" | grep -q "^$MIGRATION_NAME$"; then
        echo "⏭️  Skipping $MIGRATION_NAME (already applied)"
        SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
        continue
    fi
    
    echo "🔄 Applying $MIGRATION_NAME..."
    
    # Apply migration
    if cat "$MIGRATION_FILE" | docker exec -i jarvis-supabase-db psql -U postgres jarvis; then
        # Record migration
        docker exec jarvis-supabase-db psql -U postgres jarvis -c "INSERT INTO schema_migrations (migration_file) VALUES ('$MIGRATION_NAME');" > /dev/null
        echo "  ✅ Applied successfully"
        APPLIED_COUNT=$((APPLIED_COUNT + 1))
    else
        echo "  ❌ Failed to apply migration"
        exit 1
    fi
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Migration complete!"
echo "   Applied: $APPLIED_COUNT"
echo "   Skipped: $SKIPPED_COUNT"
echo ""
