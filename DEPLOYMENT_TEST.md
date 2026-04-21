# JARVIS Deployment Testing Guide

This document outlines the testing procedures for validating the JARVIS deployment.

## Pre-Deployment Checklist

- [ ] Docker installed and running
- [ ] Docker Compose installed
- [ ] `.env` file created and configured with API keys
- [ ] At least 4GB RAM available
- [ ] At least 10GB disk space available

## Test 1: Configuration Validation

### Objective
Verify that docker-compose.yml is valid and all configuration files are present.

### Steps

```bash
# Validate docker-compose.yml
docker-compose config

# Check .env file exists
ls -la .env

# Verify init-db.sql exists
ls -la init-db.sql

# Check scripts directory
ls -la scripts/
```

### Expected Results
- docker-compose config runs without errors
- .env file exists
- init-db.sql exists
- All deployment scripts are present

## Test 2: Initial Setup

### Objective
Run the setup script and verify initial configuration.

### Steps

**Linux/macOS:**
```bash
./scripts/setup.sh
```

**Windows (PowerShell):**
```powershell
.\scripts\start.ps1
```

### Expected Results
- Scripts are made executable
- .env file is created (if not exists)
- Required directories are created (logs, models, backups)
- Configuration validation passes

## Test 3: Service Startup

### Objective
Start all JARVIS services and verify they are running.

### Steps

**Linux/macOS:**
```bash
./scripts/start.sh
```

**Windows (PowerShell):**
```powershell
.\scripts\start.ps1
```

**Or using Make:**
```bash
make start
```

### Expected Results
- All Docker images are pulled successfully
- All services build without errors
- All containers start successfully
- Database health check passes

### Verification

```bash
# Check running containers
docker-compose ps

# Expected output:
# NAME                        STATUS
# jarvis-supabase-db         Up (healthy)
# jarvis-brain               Up
# jarvis-voice               Up
# jarvis-dashboard-api       Up
# jarvis-dashboard-frontend  Up
```

## Test 4: Database Initialization

### Objective
Verify that the database schema is initialized correctly.

### Steps

```bash
# Open database shell
./scripts/db-shell.sh

# Or
docker exec -it jarvis-supabase-db psql -U postgres jarvis
```

**In PostgreSQL shell:**
```sql
-- List all tables
\dt

-- Expected tables:
-- conversations
-- personal_profile
-- episodic_memory
-- reminders
-- audit_log

-- Check pgvector extension
\dx

-- Expected: vector extension listed

-- Check default profile
SELECT * FROM personal_profile;

-- Expected: One row with user_id='default_user'

-- Check audit log
SELECT * FROM audit_log;

-- Expected: At least one entry for database_initialization

-- Exit
\q
```

### Expected Results
- All 5 tables exist
- pgvector extension is enabled
- Default personal profile is created
- Database initialization is logged in audit_log

## Test 5: Service Health Checks

### Objective
Verify that all services are healthy and responding.

### Steps

```bash
# Run health check script
./scripts/health-check.sh

# Or check manually:

# Database health
docker exec jarvis-supabase-db pg_isready -U postgres

# API health (if implemented)
curl http://localhost:5000/health

# Dashboard accessibility
curl http://localhost:3000
```

### Expected Results
- Database is accepting connections
- API responds (or returns expected error if not fully implemented)
- Dashboard is accessible
- Health check script reports overall status as HEALTHY

## Test 6: Logging

### Objective
Verify that logging is working correctly.

### Steps

```bash
# View all logs
./scripts/logs.sh

# View specific service logs
./scripts/logs.sh brain
./scripts/logs.sh supabase-db
./scripts/logs.sh dashboard-api

# Check log files
ls -la logs/
cat logs/app.log
cat logs/error.log
cat logs/audit.log
```

### Expected Results
- Logs are being generated
- No critical errors in logs
- Log files exist in logs/ directory
- Logs are properly formatted

## Test 7: Database Backup and Restore

### Objective
Test database backup and restore functionality.

### Steps

```bash
# Create a test entry
docker exec -it jarvis-supabase-db psql -U postgres jarvis -c "INSERT INTO audit_log (action_type, details) VALUES ('test_action', '{\"test\": true}');"

# Create backup
./scripts/backup.sh

# Verify backup file exists
ls -la backups/

# Note the backup filename
BACKUP_FILE=$(ls -t backups/*.sql.gz | head -1)

# Restore from backup
./scripts/restore.sh $BACKUP_FILE

# Verify data is restored
docker exec -it jarvis-supabase-db psql -U postgres jarvis -c "SELECT * FROM audit_log WHERE action_type='test_action';"
```

### Expected Results
- Backup file is created in backups/ directory
- Backup file is compressed (.gz)
- Restore completes without errors
- Test data is present after restore

## Test 8: Database Migrations

### Objective
Test database migration functionality.

### Steps

```bash
# Check existing migrations
ls -la migrations/

# Apply migrations
./scripts/migrate.sh

# Verify migration tracking table
docker exec -it jarvis-supabase-db psql -U postgres jarvis -c "SELECT * FROM schema_migrations;"
```

### Expected Results
- Migrations are applied successfully
- schema_migrations table tracks applied migrations
- Re-running migrate.sh skips already applied migrations

## Test 9: Service Status and Monitoring

### Objective
Verify monitoring and status reporting.

### Steps

```bash
# Check service status
./scripts/status.sh

# Or
make status

# Check resource usage
docker stats --no-stream
```

### Expected Results
- All services show as "Up"
- Resource usage is within acceptable limits
- No services are restarting repeatedly

## Test 10: Service Restart

### Objective
Test stopping and restarting services.

### Steps

```bash
# Stop services
./scripts/stop.sh

# Verify services are stopped
docker-compose ps

# Start services again
./scripts/start.sh

# Verify services are running
docker-compose ps

# Check data persistence
docker exec -it jarvis-supabase-db psql -U postgres jarvis -c "SELECT COUNT(*) FROM audit_log;"
```

### Expected Results
- Services stop cleanly
- Services restart successfully
- Data persists across restarts
- No data loss

## Test 11: Development Mode

### Objective
Test development mode with attached logs.

### Steps

```bash
# Start in development mode
./scripts/dev.sh

# Or
make dev

# Observe logs in real-time
# Press Ctrl+C to stop
```

### Expected Results
- Services start with logs attached
- Logs are displayed in real-time
- Ctrl+C stops all services cleanly

## Test 12: Clean Installation

### Objective
Test complete cleanup and fresh installation.

### Steps

```bash
# Create backup first
./scripts/backup.sh

# Clean everything
./scripts/clean.sh

# Verify everything is removed
docker-compose ps
docker volume ls | grep jarvis

# Fresh start
./scripts/start.sh

# Verify fresh database
docker exec -it jarvis-supabase-db psql -U postgres jarvis -c "SELECT COUNT(*) FROM audit_log;"
```

### Expected Results
- All containers are removed
- All volumes are removed
- Fresh start creates new database
- Only initialization entries in audit_log

## Test 13: Port Configuration

### Objective
Verify that custom ports work correctly.

### Steps

```bash
# Edit .env
# Change DASHBOARD_PORT=3001
# Change API_PORT=5001
# Change DB_PORT=5433

# Restart services
./scripts/stop.sh
./scripts/start.sh

# Verify new ports
curl http://localhost:3001
curl http://localhost:5001/health
psql -h localhost -p 5433 -U postgres jarvis
```

### Expected Results
- Services start on custom ports
- Dashboard accessible on new port
- API accessible on new port
- Database accessible on new port

## Test 14: Error Handling

### Objective
Test error handling and recovery.

### Steps

```bash
# Test with missing .env
mv .env .env.backup
./scripts/start.sh
# Expected: Error message about missing .env

# Restore .env
mv .env.backup .env

# Test with Docker not running
# Stop Docker
./scripts/start.sh
# Expected: Error message about Docker not running

# Start Docker and retry
./scripts/start.sh
# Expected: Successful start
```

### Expected Results
- Clear error messages for missing configuration
- Clear error messages for Docker issues
- Graceful handling of errors
- Helpful suggestions for resolution

## Test 15: Documentation Validation

### Objective
Verify that all documentation is accurate and complete.

### Steps

```bash
# Check README exists
cat README.md

# Check DEPLOYMENT.md exists
cat DEPLOYMENT.md

# Check scripts/README.md exists
cat scripts/README.md

# Verify all commands in documentation work
# Follow quick start guide in DEPLOYMENT.md
```

### Expected Results
- All documentation files exist
- Documentation is clear and accurate
- All commands in documentation work as described
- No broken links or references

## Performance Tests

### Test 16: Database Performance

```sql
-- Connect to database
\c jarvis

-- Test vector search performance
EXPLAIN ANALYZE SELECT * FROM conversations 
WHERE embedding IS NOT NULL 
ORDER BY embedding <-> '[0.1, 0.2, ...]'::vector 
LIMIT 5;

-- Expected: Query time < 500ms

-- Test regular queries
EXPLAIN ANALYZE SELECT * FROM conversations 
WHERE session_id = 'test_session' 
ORDER BY timestamp DESC 
LIMIT 20;

-- Expected: Query time < 100ms
```

### Test 17: Resource Usage

```bash
# Monitor resource usage for 5 minutes
docker stats

# Expected:
# - CPU usage < 50% per service
# - Memory usage < 2GB total
# - No memory leaks (stable memory over time)
```

## Security Tests

### Test 18: Credential Security

```bash
# Verify no hardcoded credentials
grep -r "sk-" jarvis/ || echo "No API keys found in code"
grep -r "Bearer " jarvis/ || echo "No tokens found in code"

# Verify .env is in .gitignore
cat .gitignore | grep ".env"

# Expected: No credentials in code, .env in .gitignore
```

### Test 19: Network Security

```bash
# Check network isolation
docker network inspect jarvis-network

# Verify only required ports are exposed
docker-compose ps

# Expected: Only specified ports exposed to host
```

## Troubleshooting Common Issues

### Issue: Services won't start

**Solution:**
```bash
# Check Docker
docker info

# Check logs
./scripts/logs.sh

# Check disk space
df -h

# Check memory
free -h
```

### Issue: Database connection fails

**Solution:**
```bash
# Check database is running
docker-compose ps supabase-db

# Check database logs
./scripts/logs.sh supabase-db

# Wait for initialization (can take 30 seconds)
sleep 30
./scripts/health-check.sh
```

### Issue: Port already in use

**Solution:**
```bash
# Find process using port
lsof -i :3000
lsof -i :5000
lsof -i :5432

# Kill process or change port in .env
```

## Test Results Template

```
JARVIS Deployment Test Results
Date: _______________
Tester: _______________

[ ] Test 1: Configuration Validation - PASS/FAIL
[ ] Test 2: Initial Setup - PASS/FAIL
[ ] Test 3: Service Startup - PASS/FAIL
[ ] Test 4: Database Initialization - PASS/FAIL
[ ] Test 5: Service Health Checks - PASS/FAIL
[ ] Test 6: Logging - PASS/FAIL
[ ] Test 7: Database Backup and Restore - PASS/FAIL
[ ] Test 8: Database Migrations - PASS/FAIL
[ ] Test 9: Service Status and Monitoring - PASS/FAIL
[ ] Test 10: Service Restart - PASS/FAIL
[ ] Test 11: Development Mode - PASS/FAIL
[ ] Test 12: Clean Installation - PASS/FAIL
[ ] Test 13: Port Configuration - PASS/FAIL
[ ] Test 14: Error Handling - PASS/FAIL
[ ] Test 15: Documentation Validation - PASS/FAIL
[ ] Test 16: Database Performance - PASS/FAIL
[ ] Test 17: Resource Usage - PASS/FAIL
[ ] Test 18: Credential Security - PASS/FAIL
[ ] Test 19: Network Security - PASS/FAIL

Overall Result: PASS/FAIL

Notes:
_________________________________
_________________________________
_________________________________
```

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Automated test script
#!/bin/bash
set -e

echo "Running JARVIS deployment tests..."

# Setup
./scripts/setup.sh

# Start services
./scripts/start.sh

# Wait for services to be ready
sleep 30

# Run health check
./scripts/health-check.sh

# Run application tests
make test

# Cleanup
./scripts/stop.sh

echo "All tests passed!"
```

## Conclusion

After completing all tests, JARVIS deployment should be:
- ✅ Fully functional
- ✅ Properly configured
- ✅ Secure
- ✅ Performant
- ✅ Well-documented
- ✅ Easy to maintain

For production deployment, refer to DEPLOYMENT.md for additional security and scaling considerations.
