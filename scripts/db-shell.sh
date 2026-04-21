#!/bin/bash
# JARVIS Database Shell Script
# This script opens a PostgreSQL shell to the JARVIS database

echo "🗄️  Opening JARVIS database shell..."
echo ""
echo "💡 Useful commands:"
echo "  \\dt          - List all tables"
echo "  \\d+ table    - Describe table structure"
echo "  \\q           - Quit"
echo ""

docker exec -it jarvis-supabase-db psql -U postgres jarvis
