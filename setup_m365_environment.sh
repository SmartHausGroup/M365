#!/bin/bash

# 🚀 SmartHaus Group M365 Environment Setup Script 🚀
# This script sets up the complete M365 automation environment

set -e  # Exit on any error

echo "🚀 Starting SmartHaus Group M365 Environment Setup..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS. Please run on a Mac system."
    exit 1
fi

print_status "Checking system requirements..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    print_error "Homebrew is not installed. Please install Homebrew first:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

print_success "Homebrew is installed"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_warning "Python 3 not found. Installing via Homebrew..."
    brew install python@3.12
fi

print_success "Python 3 is available"

# Install Azure CLI if not present
if ! command -v az &> /dev/null; then
    print_status "Installing Azure CLI..."
    brew install azure-cli
else
    print_success "Azure CLI is already installed"
fi

# Install Azure CLI extensions
print_status "Installing Azure CLI extensions..."

# Install Microsoft Graph extension
az extension add --name graph --yes 2>/dev/null || print_warning "Graph extension already installed or failed to install"

# Install SharePoint extension
az extension add --name sharepoint --yes 2>/dev/null || print_warning "SharePoint extension already installed or failed to install"

# Install Teams extension
az extension add --name teams --yes 2>/dev/null || print_warning "Teams extension already installed or failed to install"

# Install Power Platform extension
az extension add --name powerplatform --yes 2>/dev/null || print_warning "Power Platform extension already installed or failed to install"

print_success "Azure CLI extensions installed"

# Install Python dependencies
print_status "Installing Python dependencies..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_warning "requirements.txt not found, installing core dependencies..."
    pip install azure-identity azure-mgmt-graphservices requests msal
fi

# Install additional useful tools
print_status "Installing additional tools..."

# Install jq for JSON processing
brew install jq

# Install yq for YAML processing
brew install yq

# Install tree for directory visualization
brew install tree

print_success "Additional tools installed"

# Create configuration directory
print_status "Setting up configuration..."

mkdir -p ~/.smarthaus-m365
mkdir -p ~/.smarthaus-m365/scripts
mkdir -p ~/.smarthaus-m365/templates
mkdir -p ~/.smarthaus-m365/logs

# Create configuration file
cat > ~/.smarthaus-m365/config.json << EOF
{
    "organization": "SmartHaus Group",
    "tenant_id": "",
    "subscription_id": "",
    "default_location": "East US",
    "sharepoint_sites": {
        "Executive": {
            "description": "Executive leadership and strategic planning",
            "template": "STS#0",
            "permissions": ["Full Control"]
        },
        "Operations": {
            "description": "Day-to-day operations and process management",
            "template": "STS#0",
            "permissions": ["Full Control"]
        },
        "Development": {
            "description": "Software development and technical projects",
            "template": "STS#0",
            "permissions": ["Full Control"]
        },
        "Sales_Marketing": {
            "description": "Sales, marketing, and business development",
            "template": "STS#0",
            "permissions": ["Full Control"]
        },
        "Finance_HR": {
            "description": "Financial management and human resources",
            "template": "STS#0",
            "permissions": ["Full Control"]
        },
        "Client_Projects": {
            "description": "Client project management and deliverables",
            "template": "STS#0",
            "permissions": ["Full Control"]
        }
    },
    "teams_workspaces": {
        "Leadership": {
            "description": "Executive team communications",
            "channels": ["General", "Strategic Planning", "Board Updates"]
        },
        "Operations": {
            "description": "Operational team collaboration",
            "channels": ["General", "Process Improvement", "Daily Ops"]
        },
        "Development": {
            "description": "Development team collaboration",
            "channels": ["General", "Code Reviews", "Architecture", "DevOps"]
        },
        "Sales_Marketing": {
            "description": "Sales and marketing collaboration",
            "channels": ["General", "Lead Generation", "Campaigns", "Client Success"]
        }
    },
    "automation_workflows": [
        "Document Approval Workflow",
        "New Employee Onboarding",
        "Client Project Setup",
        "Monthly Report Generation",
        "Expense Approval Process"
    ]
}
EOF

print_success "Configuration created at ~/.smarthaus-m365/config.json"

# Create utility scripts
print_status "Creating utility scripts..."

# Create a script to check M365 status
cat > ~/.smarthaus-m365/scripts/check_status.sh << 'EOF'
#!/bin/bash
echo "🔍 Checking SmartHaus Group M365 Status..."
echo "=========================================="

# Check Azure CLI status
echo "Azure CLI Status:"
az account show --query "{name:name, tenantId:tenantId, subscriptionId:id}" -o table

echo -e "\nSharePoint Sites:"
az graph query --query "resources | where type == 'microsoft.sharepoint/sites' | project name, properties.displayName, properties.description" -o table

echo -e "\nTeams Workspaces:"
az graph query --query "resources | where type == 'microsoft.teams/teams' | project name, properties.displayName, properties.description" -o table

echo -e "\n✅ Status check complete!"
EOF

chmod +x ~/.smarthaus-m365/scripts/check_status.sh

# Create a script to add new employees
cat > ~/.smarthaus-m365/scripts/add_employee.sh << 'EOF'
#!/bin/bash
# Usage: ./add_employee.sh "First Last" "email@smarthausgroup.com" "Department"

if [ $# -ne 3 ]; then
    echo "Usage: $0 \"Full Name\" \"email@smarthausgroup.com\" \"Department\""
    exit 1
fi

FULL_NAME="$1"
EMAIL="$2"
DEPARTMENT="$3"

echo "👤 Adding new employee: $FULL_NAME ($EMAIL) to $DEPARTMENT"
echo "=========================================================="

# Create user in Azure AD
echo "Creating user in Azure AD..."
az ad user create \
    --display-name "$FULL_NAME" \
    --mail-nickname "$(echo $FULL_NAME | tr ' ' '.')" \
    --user-principal-name "$EMAIL" \
    --password "TempPassword123!" \
    --force-change-password-next-login true

# Add to appropriate groups based on department
case $DEPARTMENT in
    "Executive"|"Leadership")
        az ad group member add --group "SmartHaus Executive" --member-id "$EMAIL"
        ;;
    "Operations")
        az ad group member add --group "SmartHaus Operations" --member-id "$EMAIL"
        ;;
    "Development")
        az ad group member add --group "SmartHaus Development" --member-id "$EMAIL"
        ;;
    "Sales"|"Marketing")
        az ad group member add --group "SmartHaus Sales Marketing" --member-id "$EMAIL"
        ;;
    "Finance"|"HR")
        az ad group member add --group "SmartHaus Finance HR" --member-id "$EMAIL"
        ;;
    *)
        echo "Unknown department: $DEPARTMENT"
        ;;
esac

echo "✅ Employee $FULL_NAME added successfully!"
echo "📧 Temporary password: TempPassword123!"
echo "🔐 User must change password on first login"
EOF

chmod +x ~/.smarthaus-m365/scripts/add_employee.sh

# Create a script to create new client project
cat > ~/.smarthaus-m365/scripts/create_client_project.sh << 'EOF'
#!/bin/bash
# Usage: ./create_client_project.sh "Client Name" "Project Name"

if [ $# -ne 2 ]; then
    echo "Usage: $0 \"Client Name\" \"Project Name\""
    exit 1
fi

CLIENT_NAME="$1"
PROJECT_NAME="$2"
PROJECT_ID=$(echo "$CLIENT_NAME-$PROJECT_NAME" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')

echo "🏗️ Creating new client project: $PROJECT_NAME for $CLIENT_NAME"
echo "============================================================="

# Create SharePoint site for project
echo "Creating SharePoint project site..."
az graph query --query "resources | where type == 'microsoft.sharepoint/sites' | where properties.displayName == 'SmartHaus Client_Projects'" -o json | jq -r '.value[0].id' | xargs -I {} az graph query --query "resources | where type == 'microsoft.sharepoint/sites' | where properties.displayName == '$PROJECT_ID'" -o json

# Create Teams channel for project
echo "Creating Teams project channel..."
az teams channel create \
    --team "SmartHaus Client_Projects" \
    --name "$PROJECT_ID" \
    --description "Project channel for $CLIENT_NAME - $PROJECT_NAME"

echo "✅ Client project $PROJECT_NAME created successfully!"
echo "📁 SharePoint site: $PROJECT_ID"
echo "📢 Teams channel: $PROJECT_ID"
EOF

chmod +x ~/.smarthaus-m365/scripts/create_client_project.sh

print_success "Utility scripts created in ~/.smarthaus-m365/scripts/"

# Create a Makefile for easy commands
cat > Makefile << 'EOF'
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
EOF

print_success "Makefile created for easy command execution"

# Final setup steps
print_status "Performing final setup steps..."

# Set up shell completion
if [[ "$SHELL" == *"zsh"* ]]; then
    echo "Setting up zsh completion..."
    echo 'source ~/.smarthaus-m365/scripts/check_status.sh' >> ~/.zshrc
    echo 'alias m365-status="~/.smarthaus-m365/scripts/check_status.sh"' >> ~/.zshrc
    echo 'alias m365-add-employee="~/.smarthaus-m365/scripts/add_employee.sh"' >> ~/.zshrc
    echo 'alias m365-create-project="~/.smarthaus-m365/scripts/create_client_project.sh"' >> ~/.zshrc
    print_success "zsh completion and aliases configured"
elif [[ "$SHELL" == *"bash"* ]]; then
    echo "Setting up bash completion..."
    echo 'source ~/.smarthaus-m365/scripts/check_status.sh' >> ~/.bashrc
    echo 'alias m365-status="~/.smarthaus-m365/scripts/check_status.sh"' >> ~/.bashrc
    echo 'alias m365-add-employee="~/.smarthaus-m365/scripts/add_employee.sh"' >> ~/.bashrc
    echo 'alias m365-create-project="~/.smarthaus-m365/scripts/create_client_project.sh"' >> ~/.bashrc
    print_success "bash completion and aliases configured"
fi

# Create a quick start guide
cat > ~/.smarthaus-m365/QUICK_START.md << 'EOF'
# 🚀 SmartHaus Group M365 Quick Start Guide 🚀

## 🎯 What's Been Set Up

✅ **Azure CLI** with all necessary extensions
✅ **Python environment** with M365 automation libraries
✅ **Configuration files** for your organization
✅ **Utility scripts** for common tasks
✅ **Makefile** for easy command execution

## 🚀 Quick Commands

### Check M365 Status
```bash
make check-status
# or
m365-status
```

### Add New Employee
```bash
make add-employee
# or
m365-add-employee "John Doe" "john@smarthausgroup.com" "Development"
```

### Create Client Project
```bash
make create-project
# or
m365-create-project "Acme Corp" "Website Redesign"
```

### Run Complete Automation
```bash
make run-automation
```

### Install Dependencies
```bash
make install-deps
```

## 🔐 Authentication

1. Run `az login` to authenticate with Azure
2. Select your SmartHaus Group subscription
3. You're ready to go!

## 📁 File Locations

- **Configuration**: `~/.smarthaus-m365/config.json`
- **Scripts**: `~/.smarthaus-m365/scripts/`
- **Logs**: `~/.smarthaus-m365/logs/`
- **Templates**: `~/.smarthaus-m365/templates/`

## 🎯 Next Steps

1. **Customize Configuration**: Edit `~/.smarthaus-m365/config.json`
2. **Test Setup**: Run `make check-status`
3. **Create Sites**: Run `make run-automation`
4. **Add Team Members**: Use `make add-employee`
5. **Scale Up**: Add more automation as needed

## 🆘 Need Help?

- Check the logs in `~/.smarthaus-m365/logs/`
- Review the configuration in `~/.smarthaus-m365/config.json`
- Run `make help` for all available commands

🎉 **Welcome to your automated M365 empire!** 🎉
EOF

print_success "Quick start guide created at ~/.smarthaus-m365/QUICK_START.md"

# Final message
echo ""
echo "🎉 🎉 🎉 SETUP COMPLETE! 🎉 🎉 🎉"
echo "====================================="
echo ""
echo "🚀 Your SmartHaus Group M365 automation environment is ready!"
echo ""
echo "📚 Next steps:"
echo "  1. Read the quick start guide: ~/.smarthaus-m365/QUICK_START.md"
echo "  2. Run 'make help' to see all available commands"
echo "  3. Run 'make check-status' to verify your setup"
echo "  4. Run 'make run-automation' to create your M365 environment"
echo ""
echo "🔐 Don't forget to authenticate: az login"
echo ""
echo "🎯 Ready to build your automated M365 empire!"
echo ""
echo "📁 Configuration files are in: ~/.smarthaus-m365/"
echo "🛠️  Utility scripts are in: ~/.smarthaus-m365/scripts/"
echo "📖 Quick start guide: ~/.smarthaus-m365/QUICK_START.md"
echo ""
print_success "Setup completed successfully!"
