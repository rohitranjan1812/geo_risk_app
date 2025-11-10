.PHONY: help build up down restart logs test clean init dev prod

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Geo Risk Application - Docker Commands"
	@echo "========================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - copy env file
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Created .env file from .env.example"; \
		echo "⚠️  Please edit .env with your configuration"; \
	else \
		echo "✓ .env file already exists"; \
	fi

build: ## Build all Docker containers
	@echo "Building containers..."
	docker-compose build

up: ## Start all services in detached mode
	@echo "Starting services..."
	docker-compose up -d
	@echo "✓ Services started"
	@echo "Application: http://localhost"
	@echo "API Docs: http://localhost/docs"

dev: setup ## Start services in development mode (with logs)
	@echo "Starting in development mode..."
	docker-compose up

down: ## Stop all services
	@echo "Stopping services..."
	docker-compose down

stop: ## Stop services without removing containers
	@echo "Stopping services..."
	docker-compose stop

restart: ## Restart all services
	@echo "Restarting services..."
	docker-compose restart

logs: ## Show logs from all services
	docker-compose logs -f

logs-backend: ## Show backend logs only
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs only
	docker-compose logs -f frontend

logs-db: ## Show database logs only
	docker-compose logs -f db

logs-nginx: ## Show nginx logs only
	docker-compose logs -f nginx

status: ## Show status of all containers
	@echo "Container Status:"
	@docker-compose ps

test: ## Run backend tests in Docker
	@echo "Running tests..."
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from backend_test
	docker-compose -f docker-compose.test.yml down

test-deployment: ## Run comprehensive deployment tests
	@echo "Running deployment validation tests..."
	@chmod +x test-deployment.sh
	./test-deployment.sh

init-db: ## Initialize database with sample data
	@echo "Initializing database..."
	docker-compose exec backend python init_db.py

shell-backend: ## Open shell in backend container
	docker-compose exec backend /bin/bash

shell-db: ## Open PostgreSQL shell
	docker-compose exec db psql -U georisk -d georisk_db

backup-db: ## Backup database to backup.sql
	@echo "Backing up database..."
	docker-compose exec -T db pg_dump -U georisk georisk_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✓ Backup created"

restore-db: ## Restore database from backup.sql (requires BACKUP_FILE variable)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Error: Please specify BACKUP_FILE=<file>"; \
		exit 1; \
	fi
	@echo "Restoring database from $(BACKUP_FILE)..."
	docker-compose exec -T db psql -U georisk georisk_db < $(BACKUP_FILE)
	@echo "✓ Database restored"

clean: ## Remove containers, networks, and volumes
	@echo "Cleaning up..."
	docker-compose down -v
	@echo "✓ Cleanup complete"

clean-all: clean ## Remove containers, networks, volumes, and images
	@echo "Removing images..."
	docker-compose down -v --rmi all
	@echo "✓ Full cleanup complete"

rebuild: ## Rebuild containers without cache
	@echo "Rebuilding containers..."
	docker-compose build --no-cache

prod: setup ## Start in production mode
	@echo "Starting in production mode..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "✓ Production services started"

prod-logs: ## Show production logs
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

prod-down: ## Stop production services
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

health: ## Check health of all services
	@echo "Checking service health..."
	@echo ""
	@echo "Nginx Proxy:"
	@curl -sf http://localhost/health && echo "  ✓ Healthy" || echo "  ✗ Unhealthy"
	@echo ""
	@echo "Backend API:"
	@curl -sf http://localhost:8000/health && echo "  ✓ Healthy" || echo "  ✗ Unhealthy"
	@echo ""
	@echo "Frontend:"
	@curl -sf http://localhost:3000/health && echo "  ✓ Healthy" || echo "  ✗ Unhealthy"
	@echo ""
	@echo "Database:"
	@docker-compose exec db pg_isready -U georisk && echo "  ✓ Healthy" || echo "  ✗ Unhealthy"

stats: ## Show resource usage statistics
	@docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" | grep georisk

update: ## Pull latest changes and restart services
	@echo "Updating application..."
	git pull
	docker-compose build
	docker-compose up -d
	@echo "✓ Application updated"

migrate: ## Run database migrations
	@echo "Running database migrations..."
	docker-compose exec backend alembic upgrade head
	@echo "✓ Migrations complete"

generate-secrets: ## Generate secure random secrets
	@echo "Generated secrets (use in .env file):"
	@echo ""
	@echo "SECRET_KEY=$$(openssl rand -base64 32)"
	@echo "POSTGRES_PASSWORD=$$(openssl rand -base64 32)"
