# 🚀 SmartHaus Group M365 Makefile 🚀

.PHONY: help clean install-deps test lint format serve-api cli pre-commit ci

help: ## Show this help message
	@echo "🚀 SmartHaus Group M365 Commands 🚀"
	@echo "==================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

clean: ## Clean up temporary files
	@echo "🧹 Cleaning up..."
	@rm -rf __pycache__ *.pyc .pytest_cache .mypy_cache
	@echo "✅ Cleanup complete!"

install-deps: ## Install project dependencies (dev)
	@echo "📦 Installing dependencies (editable + dev)..."
	@python -m pip install --upgrade pip
	@pip install -e .[dev]

test: ## Run tests
	@echo "🧪 Running tests..."
	@pytest -q --cov=src --cov-report=term-missing

lint: ## Run linters (ruff, mypy)
	@echo "🔎 Linting..."
	@ruff check .
	@mypy src

format: ## Format code (ruff format, black)
	@echo "🧹 Formatting..."
	@ruff format .
	@black .

serve-api: ## Run provisioning API locally
	@echo "🚀 Serving provisioning API on :8000"
	@uvicorn provisioning_api.main:app --reload --port 8000

cli: ## Run SmartHaus CLI
	@echo "💻 Running CLI..."
	@python -m smarthaus_cli --help

pre-commit: ## Install and run pre-commit on all files
	@echo "🔧 Setting up pre-commit hooks..."
	@pre-commit install
	@pre-commit run --all-files || true

ci: ## Run lint and tests
	@$(MAKE) lint
	@$(MAKE) test

.PHONY: build-dashboard
build-dashboard: ## Build static dashboard for Vercel (dist/)
	@echo "🛠️ Building static enterprise dashboard..."
	@rm -rf dist && mkdir -p dist
	@cp src/styles/enterprise.css dist/style.css || cp static/style.css dist/style.css
	@cp src/frontend/environment-detection.js dist/env.js
	@cp src/frontend/api-router.js dist/api.js
	@DASH_TITLE="$${DASHBOARD_TITLE:-SmartHaus M365 Automation Empire}"; \
	 API_URL="$${API_BASE_URL:-https://api.m365.smarthaus.ai}"; \
	 sed -e "s#__DASHBOARD_TITLE__#$$DASH_TITLE#g" -e "s#__API_BASE_URL__#$$API_URL#g" src/frontend/enterprise-dashboard.html > dist/index.html
	@echo "✅ Built to dist/"

.PHONY: docker-dev-up docker-dev-down docker-dev-logs
docker-dev-up: ## Start local dev API (Docker) on localhost:8000
	@./scripts/start-local-dev.sh

docker-dev-down: ## Stop local dev API
	@./scripts/stop-local-dev.sh

docker-dev-logs: ## Tail local dev API logs
	@docker compose -f docker-compose.local.yml logs -f

# Docker targets
.PHONY: docker-build docker-run docker-run-instance docker-stop-instance docker-list docker-logs docker-clean docker-stop-all

docker-build: ## Build Docker image
	@docker build -t smarthaus/m365-dashboard:latest .

docker-run: ## Run default instance on port 8000
	@PORT=8000 NAME=m365-dashboard ./scripts/start-instance.sh

docker-run-instance: ## Run named instance on specific port (NAME, PORT)
	@NAME=${NAME} PORT=${PORT} ./scripts/start-instance.sh

docker-stop-instance: ## Stop named instance (NAME)
	@NAME=${NAME} ./scripts/stop-instance.sh

docker-list: ## List running dashboard instances
	@./scripts/list-instances.sh

docker-logs: ## View logs for named instance (NAME)
	@docker compose -p ${NAME} logs -f

docker-stop-all: ## Stop all running instances
	@docker ps --filter "label=com.smarthaus.m365=1" --format '{{.Label "com.docker.compose.project"}}' | sort -u | xargs -I{} sh -c 'docker compose -p {} down || true'

docker-clean: ## Remove dangling images/containers
	@docker system prune -f

# Production ops
.PHONY: deploy-production backup-all restore-instance monitor-health scale-up logs-aggregate

deploy-production: ## Deploy a production instance (NAME, PORT)
	@NAME=${NAME} PORT=${PORT} ./scripts/deploy-production.sh

backup-all: ## Backup all instance data (to ./backups)
	@./scripts/backup-instances.sh

restore-instance: ## Restore a specific instance (NAME, ARCHIVE)
	@NAME=${NAME} ARCHIVE=${ARCHIVE} ./scripts/restore-instances.sh

monitor-health: ## Show health for all running instances
	@./scripts/monitor-health.sh

scale-up: ## Start N instances (NAME base, COUNT, PORT base)
	@NAME=${NAME} COUNT=${COUNT} PORT=${PORT} ./scripts/scale-instances.sh

logs-aggregate: ## Aggregate logs for all instances
	@docker ps --filter "label=com.smarthaus.m365=1" --format '{{.Label "com.docker.compose.project"}}' | sort -u | xargs -I{} sh -c 'echo ===== {} =====; docker compose -p {} logs --tail=200'
