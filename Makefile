.PHONY: help dev prod up down restart logs shell test clean build

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)PatchHive - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

# Development
dev: ## Start development environment
	@echo "$(BLUE)Starting development environment...$(NC)"
	docker compose up -d
	@echo "$(GREEN)✓ Development environment started!$(NC)"
	@echo "  Frontend: http://localhost:5173"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

dev-logs: ## Start dev environment and follow logs
	docker compose up

# Production
prod: ## Start production environment
	@echo "$(BLUE)Starting production environment...$(NC)"
	docker compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✓ Production environment started!$(NC)"

prod-logs: ## Start prod environment and follow logs
	docker compose -f docker-compose.prod.yml up

# Common commands
up: dev ## Alias for 'make dev'

down: ## Stop and remove containers
	@echo "$(YELLOW)Stopping containers...$(NC)"
	docker compose down
	docker compose -f docker-compose.prod.yml down 2>/dev/null || true
	@echo "$(GREEN)✓ Containers stopped$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)Restarting services...$(NC)"
	docker compose restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

restart-backend: ## Restart backend only
	docker compose restart backend

restart-frontend: ## Restart frontend only
	docker compose restart frontend-dev

logs: ## Follow logs for all services
	docker compose logs -f

logs-backend: ## Follow backend logs
	docker compose logs -f backend

logs-frontend: ## Follow frontend logs
	docker compose logs -f frontend-dev

logs-db: ## Follow database logs
	docker compose logs -f db

# Shell access
shell-backend: ## Access backend shell
	docker compose exec backend bash

shell-frontend: ## Access frontend shell
	docker compose exec frontend-dev sh

shell-db: ## Access database shell
	docker compose exec db psql -U patchhive -d patchhive

# Testing
test: ## Run all tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	docker compose exec backend pytest
	@echo "$(BLUE)Running frontend tests...$(NC)"
	docker compose exec frontend-dev npm test

test-backend: ## Run backend tests
	docker compose exec backend pytest

test-backend-cov: ## Run backend tests with coverage
	docker compose exec backend pytest --cov

test-frontend: ## Run frontend tests
	docker compose exec frontend-dev npm test

test-acceptance: ## Run acceptance tests (backend + UI)
	@echo "$(BLUE)Running backend acceptance tests...$(NC)"
	cd backend && python -m pytest tests/acceptance -q
	@echo "$(BLUE)Running frontend Playwright tests...$(NC)"
	cd frontend && npm run test:e2e

# Database
db-migrate: ## Run database migrations
	docker compose exec backend python -c "from core.database import init_db; init_db()"

db-backup: ## Backup database
	@mkdir -p backups
	docker compose exec db pg_dump -U patchhive patchhive > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Database backed up to backups/$(NC)"

db-restore: ## Restore database from backup (usage: make db-restore FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then echo "$(YELLOW)Usage: make db-restore FILE=backup.sql$(NC)"; exit 1; fi
	docker compose exec -T db psql -U patchhive -d patchhive < $(FILE)
	@echo "$(GREEN)✓ Database restored from $(FILE)$(NC)"

db-reset: ## Reset database (WARNING: Deletes all data!)
	@echo "$(YELLOW)⚠️  WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v; \
		docker compose up -d; \
		echo "$(GREEN)✓ Database reset$(NC)"; \
	else \
		echo "$(BLUE)Cancelled$(NC)"; \
	fi

# Build
build: ## Build all images
	@echo "$(BLUE)Building images...$(NC)"
	docker compose build
	@echo "$(GREEN)✓ Images built$(NC)"

build-backend: ## Build backend image
	docker compose build backend

build-frontend: ## Build frontend image
	docker compose build frontend-dev

rebuild: ## Rebuild and restart all services
	@echo "$(BLUE)Rebuilding and restarting...$(NC)"
	docker compose up -d --build
	@echo "$(GREEN)✓ Services rebuilt and restarted$(NC)"

# Cleanup
clean: ## Remove containers and volumes (WARNING: Deletes data!)
	@echo "$(YELLOW)⚠️  WARNING: This will delete all data including database!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v --remove-orphans; \
		docker compose -f docker-compose.prod.yml down -v --remove-orphans 2>/dev/null || true; \
		echo "$(GREEN)✓ Cleanup complete$(NC)"; \
	else \
		echo "$(BLUE)Cancelled$(NC)"; \
	fi

clean-images: ## Remove all images
	docker compose down --rmi all
	docker compose -f docker-compose.prod.yml down --rmi all 2>/dev/null || true

prune: ## Clean up Docker system
	docker system prune -a --volumes

# Status
ps: ## Show running containers
	docker compose ps

status: ps ## Alias for 'make ps'

stats: ## Show resource usage
	docker stats

# Health checks
health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@echo ""
	@echo "Backend:"
	@curl -s http://localhost:8000/health | jq '.' || echo "$(YELLOW)Backend not responding$(NC)"
	@echo ""
	@echo "Database:"
	@docker compose exec db pg_isready -U patchhive || echo "$(YELLOW)Database not ready$(NC)"
	@echo ""

# Install dependencies
install: ## Install dependencies (first time setup)
	@echo "$(BLUE)Installing dependencies...$(NC)"
	docker compose up -d
	docker compose exec backend pip install -r requirements.txt
	docker compose exec frontend-dev npm install
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

# Quick commands
quick-start: build dev ## Build and start development environment
	@echo "$(GREEN)✓ PatchHive is running!$(NC)"
	@echo "  Visit: http://localhost:5173"
