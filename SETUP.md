# JARVIS Setup Guide

This document provides detailed setup instructions for the JARVIS Personal AI Assistant.

## Project Structure

The project has been initialized with the following structure:

```
jarvis/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── docker-compose.yml        # Docker orchestration configuration
├── Dockerfile                # Container image definition
├── init-db.sql               # Database initialization script
├── pyproject.toml            # Python project configuration (Poetry)
├── requirements.txt          # Python dependencies (pip)
├── README.md                 # Project documentation
├── SETUP.md                  # This file
├── jarvis/                   # Main application package
│   ├── __init__.py
│   ├── config.py             # Configuration management
│   ├── logging_config.py     # Logging setup
│   ├── brain/                # LLM reasoning engine
│   │   └── __init__.py
│   ├── memory/               # Persistent storage layer
│   │   └── __init__.py
│   ├── skills/               # Executable tools
│   │   └── __init__.py
│   ├── voice/                # Speech interface
│   │   └── __init__.py
│   ├── hooks/                # Automated behaviors
│   │   └── __init__.py
│   └── dashboard/            # Web interface
│       └── __init__.py
└── logs/                     # Log files (auto-created)
    ├── app.log
    ├── error.log
    └── audit.log
```

## Prerequisites

### Required

1. **Docker & Docker Compose**
   - Docker Desktop (Windows/Mac) or Docker Engine (Linux)
   - Docker Compose v2.0+

2. **Python 3.11+**
   - For local development and testing
   - Virtual environment recommended

3. **API Keys**
   - **Claude API Key** (Anthropic) - Required for LLM reasoning
   - **Supabase Project** - Required for database (or local PostgreSQL)
   - **JWT Secret** - Required for dashboard authentication (generate a random string)

### Optional (for specific skills)

- **ElevenLabs API Key** - For text-to-speech
- **Brave Search API Key** - For web search skill
- **Weather API Key** - For weather skill
- **Google Calendar Credentials** - For calendar management
- **Gmail Credentials** - For email management
- **Home Assistant URL & Token** - For smart home control
- **GitHub Personal Access Token** - For GitHub summary skill

## Installation Steps

### 1. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set the required variables:

```bash
# Required
CLAUDE_API_KEY=sk-ant-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
JWT_SECRET=your-random-secret-string-here

# Optional (add as needed)
ELEVENLABS_API_KEY=your-elevenlabs-key
BRAVE_API_KEY=your-brave-key
WEATHER_API_KEY=your-weather-key
# ... etc
```

### 2. Database Setup

#### Option A: Using Supabase (Recommended)

1. Create a free account at [supabase.com](https://supabase.com)
2. Create a new project
3. Copy the project URL and anon key to your `.env` file
4. Run the initialization script in the Supabase SQL editor:
   ```bash
   # Copy contents of init-db.sql and paste into Supabase SQL editor
   ```

#### Option B: Using Local PostgreSQL

1. Install PostgreSQL 15+ with pgvector extension
2. Create a database named `jarvis`
3. Run the initialization script:
   ```bash
   psql -U postgres -d jarvis -f init-db.sql
   ```
4. Update `.env` with your local database connection:
   ```bash
   SUPABASE_URL=postgresql://localhost:5432/jarvis
   SUPABASE_KEY=your-postgres-password
   ```

### 3. Docker Deployment (Recommended)

Start all services with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- Supabase PostgreSQL database (if using local DB)
- JARVIS Brain service
- JARVIS Voice interface
- Dashboard API
- Dashboard frontend

Access the dashboard at: http://localhost:3000

### 4. Local Development Setup

For local development without Docker:

#### Install Dependencies

Using pip:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Using Poetry:
```bash
poetry install
poetry shell
```

#### Run Services

You'll need multiple terminal windows:

**Terminal 1 - Brain Service:**
```bash
python -m jarvis.brain.main
```

**Terminal 2 - Voice Interface:**
```bash
python -m jarvis.voice.main
```

**Terminal 3 - Dashboard API:**
```bash
python -m jarvis.dashboard.api
```

**Terminal 4 - Dashboard Frontend:**
```bash
cd jarvis/dashboard/frontend
npm install
npm start
```

## Verification

### Check Logs

Logs are stored in the `logs/` directory:

```bash
# View application logs
tail -f logs/app.log

# View error logs
tail -f logs/error.log

# View audit logs
tail -f logs/audit.log
```

### Test Configuration

Test that configuration loads correctly:

```bash
python -c "from jarvis.config import load_config; config = load_config(); print('Config loaded successfully')"
```

### Test Database Connection

```bash
python -c "from supabase import create_client; import os; client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')); print('Database connected')"
```

## Next Steps

After setup is complete:

1. **Configure Skills**: Add API keys for the skills you want to use
2. **Test Voice**: Say "Hey Jarvis" to test wake word detection
3. **Access Dashboard**: Open http://localhost:3000 and log in
4. **Run Tests**: Execute `pytest` to verify all components

## Troubleshooting

### Docker Issues

**Services won't start:**
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Rebuild containers
docker-compose up --build
```

**Port conflicts:**
- Check if ports 3000, 5000, 5432, 8000 are available
- Modify ports in `docker-compose.yml` if needed

### Database Issues

**Connection refused:**
- Verify Supabase credentials in `.env`
- Check that database service is running
- Ensure pgvector extension is enabled

**Schema not initialized:**
```bash
# Re-run initialization script
psql -f init-db.sql
```

### Voice Issues

**Wake word not detected:**
- Check microphone permissions
- Verify `VOICE_ENABLED=true` in `.env`
- Check audio device access (Docker requires `--privileged`)

**STT not working:**
- Whisper model downloads on first use (may take time)
- Check internet connection for model download
- Verify sufficient disk space for models

### Import Errors

**Module not found:**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=$PWD

# Or install in development mode
pip install -e .
```

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CLAUDE_API_KEY` | Yes | - | Claude API key |
| `SUPABASE_URL` | Yes | - | Supabase project URL |
| `SUPABASE_KEY` | Yes | - | Supabase anon/service key |
| `JWT_SECRET` | Yes | - | JWT secret for auth |
| `LLM_MODEL` | No | claude-sonnet-4-20250514 | Claude model |
| `VOICE_ENABLED` | No | true | Enable voice |
| `WAKE_WORD` | No | Hey Jarvis | Wake word |
| `DASHBOARD_PORT` | No | 3000 | Dashboard port |
| `LOG_LEVEL` | No | INFO | Logging level |

### Logging Levels

- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

### Log Files

- `logs/app.log`: All application logs (JSON format)
- `logs/error.log`: Error-level logs only (JSON format)
- `logs/audit.log`: Security and action audit trail (JSON format)

Logs rotate daily and are kept for 30 days.

## Security Notes

- Never commit `.env` file to version control
- Use strong, random JWT secret
- Rotate API keys regularly
- Review audit logs periodically
- Keep dependencies updated

## Support

For issues and questions:
- Check the troubleshooting section above
- Review logs in `logs/` directory
- Consult the main README.md
- Check Docker Compose logs: `docker-compose logs`

## Development

### Code Style

```bash
# Format code
black jarvis/

# Lint code
flake8 jarvis/

# Type checking
mypy jarvis/
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=jarvis --cov-report=html

# Specific test types
pytest tests/unit/
pytest tests/integration/
pytest tests/property/
```

### Adding New Skills

1. Create skill class in `jarvis/skills/`
2. Extend `Skill` base class
3. Implement `execute()` method
4. Register skill in skill registry
5. Add tests in `tests/unit/test_skills.py`

## License

[Your License Here]
