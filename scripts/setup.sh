#!/bin/bash
# JARVIS Initial Setup Script
# This script performs initial setup for JARVIS

set -e

echo "🤖 JARVIS Personal AI Assistant - Initial Setup"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed!"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed!"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Make scripts executable
echo "📝 Making scripts executable..."
chmod +x scripts/*.sh
echo "✅ Scripts are now executable"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your API keys:"
    echo "   - LLM_API_KEY (Anthropic Claude API key)"
    echo "   - SUPABASE_URL (Supabase project URL)"
    echo "   - SUPABASE_KEY (Supabase anonymous key)"
    echo "   - JWT_SECRET (Random secret for authentication)"
    echo ""
    echo "Optional API keys for additional features:"
    echo "   - TTS_API_KEY (ElevenLabs for text-to-speech)"
    echo "   - PORCUPINE_ACCESS_KEY (Picovoice for wake word)"
    echo "   - BRAVE_API_KEY (Brave Search)"
    echo "   - WEATHER_API_KEY (Weather data)"
    echo "   - GITHUB_TOKEN (GitHub integration)"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p logs
mkdir -p models
mkdir -p backups
echo "✅ Directories created"
echo ""

# Check if .env has required keys
if [ -f .env ]; then
    echo "🔍 Checking .env configuration..."
    
    MISSING_KEYS=()
    
    if ! grep -q "^LLM_API_KEY=..*" .env; then
        MISSING_KEYS+=("LLM_API_KEY")
    fi
    
    if ! grep -q "^SUPABASE_URL=..*" .env; then
        MISSING_KEYS+=("SUPABASE_URL")
    fi
    
    if ! grep -q "^SUPABASE_KEY=..*" .env; then
        MISSING_KEYS+=("SUPABASE_KEY")
    fi
    
    if ! grep -q "^JWT_SECRET=..*" .env; then
        MISSING_KEYS+=("JWT_SECRET")
    fi
    
    if [ ${#MISSING_KEYS[@]} -gt 0 ]; then
        echo "⚠️  Warning: The following required keys are not configured in .env:"
        for key in "${MISSING_KEYS[@]}"; do
            echo "   - $key"
        done
        echo ""
        echo "Please edit .env and add these keys before starting JARVIS."
        echo ""
    else
        echo "✅ All required keys are configured"
        echo ""
    fi
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys (if not done already)"
echo "  2. Start JARVIS: ./scripts/start.sh or make start"
echo "  3. Access dashboard: http://localhost:3000"
echo ""
echo "Useful commands:"
echo "  make help          - Show all available commands"
echo "  make start         - Start JARVIS"
echo "  make stop          - Stop JARVIS"
echo "  make logs          - View logs"
echo "  make status        - Check service status"
echo ""
