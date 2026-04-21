# JARVIS Quick Start Guide

Get JARVIS up and running in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- 4GB RAM available
- 10GB disk space

## Quick Start (3 Steps)

### 1. Configure

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your favorite editor
```

**Required API Keys:**
- `LLM_API_KEY` - Get from [Anthropic](https://console.anthropic.com/)
- `SUPABASE_URL` - Get from [Supabase](https://supabase.com/)
- `SUPABASE_KEY` - Get from [Supabase](https://supabase.com/)
- `JWT_SECRET` - Any random string (e.g., `openssl rand -hex 32`)

### 2. Start

**Linux/macOS:**
```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

**Windows (PowerShell):**
```powershell
.\scripts\start.ps1
```

**Using Make:**
```bash
make start
```

### 3. Access

- **Dashboard**: http://localhost:3000
- **API**: http://localhost:5000
- **Database**: localhost:5432

## Common Commands

```bash
# View logs
./scripts/logs.sh

# Check status
./scripts/status.sh

# Stop JARVIS
./scripts/stop.sh

# Backup database
./scripts/backup.sh

# Health check
./scripts/health-check.sh
```

## Using Make

```bash
make help      # Show all commands
make start     # Start JARVIS
make stop      # Stop JARVIS
make logs      # View logs
make status    # Check status
make backup    # Backup database
make test      # Run tests
```

## Troubleshooting

### Services won't start?

```bash
# Check Docker is running
docker info

# Check logs
./scripts/logs.sh

# Run health check
./scripts/health-check.sh
```

### Database connection issues?

```bash
# Wait 30 seconds for initialization
sleep 30

# Check database
./scripts/db-shell.sh
```

### Port already in use?

Edit `.env` and change ports:
```bash
DASHBOARD_PORT=3001
API_PORT=5001
DB_PORT=5433
```

## Next Steps

1. **Configure Voice** (Optional)
   - Add `TTS_API_KEY` for text-to-speech
   - Add `PORCUPINE_ACCESS_KEY` for wake word

2. **Add Skills** (Optional)
   - Add `BRAVE_API_KEY` for web search
   - Add `WEATHER_API_KEY` for weather
   - Add `GITHUB_TOKEN` for GitHub integration

3. **Read Documentation**
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Full deployment guide
   - [README.md](README.md) - Architecture and features
   - [scripts/README.md](scripts/README.md) - Script reference

## Getting Help

- Check logs: `./scripts/logs.sh`
- Run health check: `./scripts/health-check.sh`
- Read [DEPLOYMENT.md](DEPLOYMENT.md)
- Read [DEPLOYMENT_TEST.md](DEPLOYMENT_TEST.md)

## Clean Start

To start fresh:

```bash
# Backup first!
./scripts/backup.sh

# Clean everything
./scripts/clean.sh

# Start fresh
./scripts/start.sh
```

---

**That's it! You're ready to use JARVIS! 🤖**

For detailed information, see [DEPLOYMENT.md](DEPLOYMENT.md)
