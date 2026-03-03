# ─────────────────────────────────────────────
# PIEE — Makefile
# ─────────────────────────────────────────────

.DEFAULT_GOAL := help
SHELL := /bin/bash

# ── Variables ─────────────────────────────────
PYTHON   := python3
PIP      := pip3
UVICORN  := uvicorn
BUN      := bun
NPM      := npm
DOCKER   := docker compose

API_PORT := 8000
DASH_PORT := 3000

# ── Colors ────────────────────────────────────
BOLD  := \033[1m
GREEN := \033[32m
CYAN  := \033[36m
RESET := \033[0m

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Help
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

.PHONY: help
help: ## Show this help
	@echo ""
	@echo "$(BOLD)PIEE$(RESET) — Hybrid AI Infrastructure Platform"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-18s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Setup
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

.PHONY: install
install: install-api install-dashboard ## Install all dependencies

.PHONY: install-api
install-api: ## Install backend dependencies
	@echo "$(GREEN)→ Installing backend dependencies…$(RESET)"
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

.PHONY: install-dashboard
install-dashboard: ## Install dashboard dependencies
	@echo "$(GREEN)→ Installing dashboard dependencies…$(RESET)"
	cd dashboard && $(BUN) install 2>/dev/null || $(NPM) install

.PHONY: setup
setup: install db-setup env ## Full project setup (install + db + env)
	@echo "$(GREEN)✓ Setup complete$(RESET)"

.PHONY: env
env: ## Create .env from .env.example (if missing)
	@[ -f .env ] || (cp .env.example .env && echo "$(GREEN)→ Created .env from .env.example$(RESET)")
	@[ -f .env ] && echo "$(CYAN)  .env already exists$(RESET)" || true

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

.PHONY: db-generate
db-generate: ## Generate Prisma client
	@echo "$(GREEN)→ Generating Prisma client…$(RESET)"
	$(PYTHON) -m prisma generate

.PHONY: db-push
db-push: ## Push schema to database
	@echo "$(GREEN)→ Pushing schema to database…$(RESET)"
	$(PYTHON) -m prisma db push

.PHONY: db-setup
db-setup: db-generate db-push ## Generate client + push schema

.PHONY: db-studio
db-studio: ## Open Prisma Studio
	$(PYTHON) -m prisma studio

.PHONY: db-reset
db-reset: ## Reset database (destructive!)
	@echo "$(BOLD)⚠  This will delete all data.$(RESET)"
	@read -p "Continue? [y/N] " ans && [ "$${ans}" = "y" ]
	rm -f dev.db dev.db-journal
	$(MAKE) db-setup

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Development
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

.PHONY: dev
dev: ## Start API + Dashboard (parallel)
	@echo "$(GREEN)→ Starting PIEE…$(RESET)"
	@$(MAKE) -j2 dev-api dev-dashboard

.PHONY: dev-api
dev-api: ## Start backend (port $(API_PORT))
	$(UVICORN) app.main:app --host 0.0.0.0 --port $(API_PORT) --reload

.PHONY: dev-dashboard
dev-dashboard: ## Start dashboard (port $(DASH_PORT))
	cd dashboard && $(BUN) run dev 2>/dev/null || $(NPM) run dev

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Build
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

.PHONY: build
build: build-dashboard ## Build all artifacts

.PHONY: build-dashboard
build-dashboard: ## Build dashboard for production
	@echo "$(GREEN)→ Building dashboard…$(RESET)"
	cd dashboard && $(BUN) run build 2>/dev/null || $(NPM) run build

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Docker
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

.PHONY: docker-up
docker-up: ## Start all services via Docker
	@echo "$(GREEN)→ Starting Docker services…$(RESET)"
	$(DOCKER) up -d --build

.PHONY: docker-down
docker-down: ## Stop all Docker services
	$(DOCKER) down

.PHONY: docker-logs
docker-logs: ## Tail Docker logs
	$(DOCKER) logs -f

.PHONY: docker-build
docker-build: ## Build Docker images (no start)
	$(DOCKER) build

.PHONY: docker-restart
docker-restart: docker-down docker-up ## Rebuild and restart Docker

.PHONY: docker-ps
docker-ps: ## Show running containers
	$(DOCKER) ps

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Clean
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

.PHONY: clean
clean: ## Remove build artifacts and caches
	@echo "$(GREEN)→ Cleaning…$(RESET)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf dashboard/.next
	rm -rf sdk/dist
	@echo "$(GREEN)✓ Clean$(RESET)"

.PHONY: clean-all
clean-all: clean ## Deep clean (includes node_modules, venv)
	rm -rf dashboard/node_modules
	rm -rf sdk/node_modules
	rm -rf .venv venv
	$(DOCKER) down -v --rmi local 2>/dev/null || true
	@echo "$(GREEN)✓ Deep clean complete$(RESET)"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Code Quality & Testing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

.PHONY: lint
lint: ## Run linters (backend and frontend)
	@echo "$(GREEN)→ Linting backend (ruff)…$(RESET)"
	ruff check .
	@echo "$(GREEN)→ Linting frontend (eslint)…$(RESET)"
	cd dashboard && $(BUN) run lint 2>/dev/null || $(NPM) run lint

.PHONY: format
format: ## Run formatters (backend and frontend)
	@echo "$(GREEN)→ Formatting backend (ruff)…$(RESET)"
	ruff format .
	@echo "$(GREEN)→ Formatting frontend (prettier)…$(RESET)"
	cd dashboard && $(BUN) run format:check 2>/dev/null || $(BUN) run format 2>/dev/null || $(NPM) run format

.PHONY: test
test: ## Run backend tests
	@echo "$(GREEN)→ Running backend tests (pytest)…$(RESET)"
	pytest
