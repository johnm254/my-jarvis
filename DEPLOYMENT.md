# JARVIS Deployment Guide

This guide provides comprehensive instructions for deploying and managing the JARVIS Personal AI Assistant system.

## Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- At least 4GB RAM available
- 10GB free disk space
- Linux, macOS, or Windows with WSL2

## Quick Start

### 1. Configure Environment Variables

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required
LLM_API_KEY=your_anthropic_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
JWT_SECRET=your_random_secret_key

# Optional (for specific features)
TTS_API_KEY=your_elevenlabs_api_key
PORCUPINE_ACCESS_KEY=your_porcupine_key
BRAVE_API_KEY=your_brave_api_key
WEATHER_API_KEY=your_weather_api_key
GITHUB_TOKEN=your_github_token
```

### 2. Start JARVIS

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

This will:
- Pull required Docker images
- Build JARVIS services
- Initialize the database
- Start all services

### 3. Access JARVIS

- **Dashboard**: http://localhost:3000
- **API**: http://localhost:5000
- **Database**: localhost:5432

## Deployment Scripts

### Start Services

```bash
./scripts/start.sh
```

Starts all JARVIS services in detached mode.

### Stop Services

```bash
./scripts/stop.sh
```

Stops all JARVIS services without removing data.

### Development Mode

```bash
./scripts/dev.sh
```

Starts JARVIS with logs attached for development and debugging.

### View Logs

```bash
# All services
./scripts/logs.sh

# Specific service
./scripts/logs.sh brain
./scripts/logs.sh dashboard-api
./scripts/logs.sh supabase-db
```

### Check Status

```bash
./scripts/status.sh
```

Shows the status of all services, resource usage, and network information.

### Database Operations

#### Open Database Shell

```bash
./scripts/db-shell.sh
```

Opens a PostgreSQL shell to the JARVIS database.

#### Backup Database

```bash
./scripts/backup.sh
```

Creates a compressed backup of the database in the `backups/` directory.

#### Restore Database

```bash
./scripts/restore.sh backups/jarvis_backup_20240115_120000.sql.gz
```

Restores the database from a backup file.

### Clean Installation

```bash
./scripts/clean.sh
```

⚠️ **WARNING**: This removes all containers, volumes, and data. Use with caution!

## Service Architecture

### Services

1. **supabase-db**: PostgreSQL database with pgvector extension
2. **brain**: Main reasoning engine with Claude API integration
3. **voice**: Voice interface with wake word detection, STT, and TTS
4. **dashboard-api**: Backend API for web dashboard
5. **dashboard-frontend**: React-based web interface

### Ports

- `3000`: Dashboard frontend
- `5000`: Dashboard API
- `5432`: PostgreSQL database
- `8000`: Brain service (internal)

### Volumes

- `supabase-db-data`: Persistent database storage
- `./logs`: Application logs
- `./models`: Whisper STT models

## Configuration

### Environment Variables

#### Required

- `LLM_API_KEY`: Anthropic API key for Claude
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase anonymous key
- `JWT_SECRET`: Secret key for JWT authentication

#### Optional

- `TTS_API_KEY`: ElevenLabs API key for text-to-speech
- `PORCUPINE_ACCESS_KEY`: Picovoice access key for wake word detection
- `VOICE_ENABLED`: Enable/disable voice interface (default: true)
- `BRAVE_API_KEY`: Brave Search API key
- `WEATHER_API_KEY`: Weather API key
- `GITHUB_TOKEN`: GitHub personal access token
- `DASHBOARD_PORT`: Dashboard port (default: 3000)
- `LOG_LEVEL`: Logging level (default: INFO)

### Docker Compose Configuration

The `docker-compose.yml` file defines all services and their configurations. Key settings:

- **Health checks**: Database has health checks to ensure proper startup order
- **Restart policy**: Services restart automatically unless stopped
- **Volume mounts**: Code and logs are mounted for easy access
- **Network**: All services communicate on the `jarvis-network` bridge

## Database Schema

The database is automatically initialized with the following tables:

- `conversations`: Conversation history with vector embeddings
- `personal_profile`: User preferences and learned behaviors
- `episodic_memory`: Interaction logs with timestamps
- `reminders`: Scheduled reminders
- `audit_log`: Security and action audit trail

See `init-db.sql` for the complete schema.

## Troubleshooting

### Services Won't Start

1. Check Docker is running: `docker info`
2. Check `.env` file exists and has required keys
3. Check port availability: `lsof -i :3000,5000,5432`
4. View logs: `./scripts/logs.sh`

### Database Connection Issues

1. Check database is healthy: `docker-compose ps`
2. Wait for database initialization (can take 10-30 seconds)
3. Check database logs: `./scripts/logs.sh supabase-db`
4. Verify connection: `./scripts/db-shell.sh`

### Voice Interface Not Working

1. Check audio device access: `docker-compose logs voice`
2. Verify `VOICE_ENABLED=true` in `.env`
3. Check API keys: `TTS_API_KEY` and `PORCUPINE_ACCESS_KEY`
4. Ensure audio device is available: `/dev/snd` on Linux

### Dashboard Not Accessible

1. Check service is running: `docker-compose ps dashboard-frontend`
2. Check port is not in use: `lsof -i :3000`
3. Verify API connection: `curl http://localhost:5000/health`
4. Check logs: `./scripts/logs.sh dashboard-frontend`

### Out of Memory

1. Check resource usage: `./scripts/status.sh`
2. Increase Docker memory limit (Docker Desktop settings)
3. Stop unused services: `docker-compose stop voice` (if not using voice)

## Monitoring

### Application Logs

Logs are stored in the `logs/` directory:

- `logs/app.log`: General application logs
- `logs/error.log`: Error logs
- `logs/audit.log`: Security audit logs

### Database Monitoring

```sql
-- Connect to database
./scripts/db-shell.sh

-- Check conversation count
SELECT COUNT(*) FROM conversations;

-- Check recent interactions
SELECT timestamp, user_input, confidence_score 
FROM conversations 
ORDER BY timestamp DESC 
LIMIT 10;

-- Check memory usage
SELECT pg_size_pretty(pg_database_size('jarvis'));
```

### Resource Monitoring

```bash
# Real-time resource usage
docker stats

# Service status
./scripts/status.sh

# Disk usage
docker system df
```

## Backup and Recovery

### Regular Backups

Set up a cron job for automatic backups:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/jarvis && ./scripts/backup.sh
```

### Disaster Recovery

1. Stop services: `./scripts/stop.sh`
2. Restore database: `./scripts/restore.sh backups/latest.sql.gz`
3. Start services: `./scripts/start.sh`
4. Verify data: `./scripts/db-shell.sh`

## Upgrading

### Update JARVIS

```bash
# Pull latest code
git pull

# Rebuild services
docker-compose build

# Restart services
./scripts/stop.sh
./scripts/start.sh
```

### Database Migrations

Database migrations are stored in `migrations/` directory:

```bash
# Apply migration
cat migrations/001_add_semantic_search_function.sql | docker exec -i jarvis-supabase-db psql -U postgres jarvis
```

## Security Best Practices

1. **Change default passwords**: Update `POSTGRES_PASSWORD` in `.env`
2. **Secure JWT secret**: Use a strong random string for `JWT_SECRET`
3. **Restrict network access**: Use firewall rules to limit external access
4. **Regular backups**: Set up automated backups
5. **Monitor audit logs**: Review `audit_log` table regularly
6. **Update dependencies**: Keep Docker images and Python packages updated
7. **Encrypt at rest**: Enable disk encryption for sensitive data

## Production Deployment

### Recommended Configuration

For production deployment, consider:

1. **Use external database**: Replace `supabase-db` with managed PostgreSQL
2. **Add reverse proxy**: Use Nginx or Traefik for SSL/TLS
3. **Enable monitoring**: Add Prometheus and Grafana
4. **Set up logging**: Use centralized logging (ELK stack, Loki)
5. **Configure backups**: Automated daily backups with retention policy
6. **Use secrets management**: Vault or AWS Secrets Manager
7. **Enable rate limiting**: Protect API endpoints
8. **Set resource limits**: Configure CPU and memory limits in docker-compose.yml

### Example Production docker-compose.yml

```yaml
services:
  brain:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Support

For issues and questions:

1. Check logs: `./scripts/logs.sh`
2. Review troubleshooting section above
3. Check GitHub issues
4. Consult README.md for architecture details

## License

See LICENSE file for details.
