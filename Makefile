.PHONY: help start stop restart logs status backup restore clean dev db-shell test

help: ## Show this help message
	@echo "JARVIS Personal AI Assistant - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

start: ## Start all JARVIS services
	@./scripts/start.sh

stop: ## Stop all JARVIS services
	@./scripts/stop.sh

restart: stop start ## Restart all JARVIS services

logs: ## View logs from all services (Ctrl+C to exit)
	@./scripts/logs.sh

status: ## Show status of all services
	@./scripts/status.sh

backup: ## Create database backup
	@./scripts/backup.sh

restore: ## Restore database from backup (usage: make restore BACKUP=path/to/backup.sql.gz)
	@./scripts/restore.sh $(BACKUP)

clean: ## Remove all containers, volumes, and data (WARNING: destructive)
	@./scripts/clean.sh

dev: ## Start JARVIS in development mode with logs attached
	@./scripts/dev.sh

db-shell: ## Open PostgreSQL shell to JARVIS database
	@./scripts/db-shell.sh

test: ## Run test suite
	@docker-compose exec brain pytest tests/ -v

test-coverage: ## Run tests with coverage report
	@docker-compose exec brain pytest tests/ --cov=jarvis --cov-report=html --cov-report=term

build: ## Build all Docker images
	@docker-compose build

pull: ## Pull latest Docker images
	@docker-compose pull

ps: ## Show running containers
	@docker-compose ps

down: ## Stop and remove containers (keeps volumes)
	@docker-compose down

down-volumes: ## Stop and remove containers and volumes (WARNING: removes data)
	@docker-compose down -v

logs-brain: ## View logs from brain service
	@./scripts/logs.sh brain

logs-db: ## View logs from database service
	@./scripts/logs.sh supabase-db

logs-api: ## View logs from dashboard API service
	@./scripts/logs.sh dashboard-api

logs-voice: ## View logs from voice service
	@./scripts/logs.sh voice

setup: ## Initial setup (copy .env.example to .env)
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file from .env.example"; \
		echo "⚠️  Please edit .env and add your API keys"; \
	else \
		echo "⚠️  .env file already exists"; \
	fi

install-hooks: ## Make all scripts executable
	@chmod +x scripts/*.sh
	@echo "✅ All scripts are now executable"
