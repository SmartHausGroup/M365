# 🚀 SmartHaus Group M365 Automation Makefile 🚀

.PHONY: help setup check-status add-employee create-project run-automation clean

help: ## Show this help message
	@echo "🚀 SmartHaus Group M365 Automation Commands 🚀"
	@echo "=============================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Set up the complete M365 environment
	@echo "🚀 Setting up M365 environment..."
	@chmod +x setup_m365_environment.sh
	@./setup_m365_environment.sh

check-status: ## Check current M365 status
	@echo "🔍 Checking M365 status..."
	@~/.smarthaus-m365/scripts/check_status.sh

add-employee: ## Add a new employee (interactive)
	@echo "👤 Adding new employee..."
	@read -p "Full Name: " name; \
	read -p "Email: " email; \
	read -p "Department: " dept; \
	~/.smarthaus-m365/scripts/add_employee.sh "$$name" "$$email" "$$dept"

create-project: ## Create a new client project (interactive)
	@echo "🏗️ Creating new client project..."
	@read -p "Client Name: " client; \
	read -p "Project Name: " project; \
	~/.smarthaus-m365/scripts/create_client_project.sh "$$client" "$$project"

run-automation: ## Run the complete M365 automation
	@echo "🤖 Running M365 automation..."
	@source venv/bin/activate && python m365_automation.py

manual-setup: ## Run the manual setup guide (opens admin centers)
	@echo "🛠️ Running manual setup guide..."
	@source venv/bin/activate && python m365_admin_helper.py

clean: ## Clean up temporary files
	@echo "🧹 Cleaning up..."
	@rm -rf __pycache__
	@rm -rf *.pyc
	@rm -rf .pytest_cache
	@echo "✅ Cleanup complete!"

install-deps: ## Install Python dependencies
	@echo "📦 Installing dependencies..."
	@source venv/bin/activate && pip install -r requirements.txt

test: ## Run tests
	@echo "🧪 Running tests..."
	@source venv/bin/activate && python -m pytest tests/ -v

deploy: ## Deploy to production (use with caution)
	@echo "🚀 Deploying to production..."
	@echo "⚠️  This will make changes to your production M365 environment!"
	@read -p "Are you sure? Type 'YES' to continue: " confirm; \
	if [ "$$confirm" = "YES" ]; then \
		source venv/bin/activate && python m365_automation.py; \
	else \
		echo "Deployment cancelled."; \
	fi
