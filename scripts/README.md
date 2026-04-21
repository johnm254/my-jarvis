# JARVIS Deployment Scripts

This directory contains utility scripts for managing the JARVIS Personal AI Assistant system.

## Quick Reference

| Script | Description | Usage |
|--------|-------------|-------|
| `setup.sh` | Initial setup and configuration | `./scripts/setup.sh` |
| `start.sh` | Start all services | `./scripts/start.sh` |
| `stop.sh` | Stop all services | `./scripts/stop.sh` |
| `dev.sh` | Start in development mode | `./scripts/dev.sh` |
| `logs.sh` | View service logs | `./scripts/logs.sh [service]` |
| `status.sh` | Check service status | `./scripts/status.sh` |
| `health-check.sh` | Comprehensive health check | `./scripts/health-check.sh` |
| `backup.sh` | Backup database | `./scripts/backup.sh` |
| `restore.sh` | Restore database | `./scripts/restore.sh <file>` |
| `migrate.sh` | Apply database migrations | `./scripts/migrate.sh` |
| `db-shell.sh` | Open database shell | `./scripts/db-shell.sh` |
| `clean.sh` | Remove all data (destructive) | `./scripts/clean.sh` |

## Detailed Usage

### Initial Setup

```bash
# Run initial setup
./scripts/setup.sh

# This will:
# - Check Docker installation
# - Make scripts executable
# - Create .env file from template
# - Create required directories
# - Validate configuration
```

### Starting and Stopping

```bash
# Start JARVIS (detached mode)
./scripts/start.sh

# Start JARVIS (development mode with logs)
./scripts/dev.sh

# Stop JARVIS
./scripts/stop.sh
```

### Monitoring

```bash
# View all logs
./scripts/logs.sh

# View specific service logs
./scripts/logs.sh brain
./scripts/logs.sh supabase-db
./scripts/logs.sh dashboard-api

# Check service status
./scripts/status.sh

# Comprehensive health check
./scripts/health-check.sh
```

### Database Operations

```bash
# Open PostgreSQL shell
./scripts/db-shell.sh

# Create backup
./scripts/backup.sh
# Creates: backups/jarvis_backup_YYYYMMDD_HHMMSS.sql.gz

# Restore from backup
./scripts/restore.sh backups/jarvis_backup_20240115_120000.sql.gz

# Apply migrations
./scripts/migrate.sh
```

### Maintenance

```bash
# Clean all data (WARNING: destructive)
./scripts/clean.sh
# This removes:
# - All containers
# - All volumes (database data)
# - All logs
```

## Using Make Commands

Alternatively, you can use the Makefile for easier command execution:

```bash
# Show all available commands
make help

# Start JARVIS
make start

# Stop JARVIS
make stop

# View logs
make logs

# Check status
make status

# Create backup
make backup

# Restore backup
make restore BACKUP=backups/jarvis_backup_20240115_120000.sql.gz

# Run tests
make test

# Development mode
make dev
```

## Script Permissions

All scripts need execute permissions. Run the setup script or:

```bash
chmod +x scripts/*.sh
```

Or use:

```bash
make install-hooks
```

## Environment Variables

Scripts read configuration from `.env` file. Required variables:

- `LLM_API_KEY`: Anthropic Claude API key
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase anonymous key
- `JWT_SECRET`: Secret for JWT authentication
- `POSTGRES_PASSWORD`: Database password

Optional variables:

- `DASHBOARD_PORT`: Dashboard port (default: 3000)
- `API_PORT`: API port (default: 5000)
- `BRAIN_PORT`: Brain service port (default: 8000)
- `DB_PORT`: Database port (default: 5432)

## Troubleshooting

### Scripts not executable

```bash
chmod +x scripts/*.sh
```

### Docker not running

```bash
# Check Docker status
docker info

# Start Docker (varies by OS)
# macOS: Open Docker Desktop
# Linux: sudo systemctl start docker
```

### Services not starting

```bash
# Check logs
./scripts/logs.sh

# Check status
./scripts/status.sh

# Run health check
./scripts/health-check.sh
```

### Database connection issues

```bash
# Check database is running
docker-compose ps supabase-db

# Check database logs
./scripts/logs.sh supabase-db

# Try connecting manually
./scripts/db-shell.sh
```

## Best Practices

1. **Always backup before major changes**
   ```bash
   ./scripts/backup.sh
   ```

2. **Check health regularly**
   ```bash
   ./scripts/health-check.sh
   ```

3. **Monitor logs for errors**
   ```bash
   ./scripts/logs.sh | grep -i error
   ```

4. **Use development mode for debugging**
   ```bash
   ./scripts/dev.sh
   ```

5. **Apply migrations after updates**
   ```bash
   ./scripts/migrate.sh
   ```

## Automation

### Automated Backups

Add to crontab for daily backups:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/jarvis && ./scripts/backup.sh
```

### Automated Health Checks

Add to crontab for hourly health checks:

```bash
# Add hourly health check
0 * * * * cd /path/to/jarvis && ./scripts/health-check.sh || echo "JARVIS health check failed" | mail -s "JARVIS Alert" admin@example.com
```

## Support

For issues with scripts:

1. Check script has execute permissions
2. Verify Docker is running
3. Check `.env` file exists and is configured
4. Review logs: `./scripts/logs.sh`
5. Run health check: `./scripts/health-check.sh`

For more information, see:
- [DEPLOYMENT.md](../DEPLOYMENT.md) - Comprehensive deployment guide
- [README.md](../README.md) - Project overview and architecture
