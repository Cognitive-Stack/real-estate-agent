# Makefile for real-estate-agent project using uv
# A fast Python package installer and resolver

.PHONY: help init install install-dev add remove update lock run test test-azure lint format clean clean-all migrate-from-poetry

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Project initialization
init: ## Initialize the project with uv
	@echo "Initializing project with uv..."
	uv init --name real-estate-agent --python 3.12
	@echo "Project initialized successfully!"

# Install dependencies
install: ## Install production dependencies
	@echo "Installing production dependencies..."
	uv pip install -e .

install-dev: ## Install development dependencies
	@echo "Installing development dependencies..."
	uv pip install -e ".[dev]"

# Dependency management
add: ## Add a package (usage: make add PACKAGE=package_name)
	@if [ -z "$(PACKAGE)" ]; then \
		echo "Error: PACKAGE variable is required. Usage: make add PACKAGE=package_name"; \
		exit 1; \
	fi
	@echo "Adding package: $(PACKAGE)"
	uv add $(PACKAGE)

add-dev: ## Add a development package (usage: make add-dev PACKAGE=package_name)
	@if [ -z "$(PACKAGE)" ]; then \
		echo "Error: PACKAGE variable is required. Usage: make add-dev PACKAGE=package_name"; \
		exit 1; \
	fi
	@echo "Adding development package: $(PACKAGE)"
	uv add --dev $(PACKAGE)

remove: ## Remove a package (usage: make remove PACKAGE=package_name)
	@if [ -z "$(PACKAGE)" ]; then \
		echo "Error: PACKAGE variable is required. Usage: make remove PACKAGE=package_name"; \
		exit 1; \
	fi
	@echo "Removing package: $(PACKAGE)"
	uv remove $(PACKAGE)

update: ## Update all dependencies
	@echo "Updating all dependencies..."
	uv lock --upgrade
	uv sync

lock: ## Generate/update lock file
	@echo "Generating lock file..."
	uv lock

sync: ## Sync dependencies with lock file
	@echo "Syncing dependencies with lock file..."
	uv sync

# Development tasks
run: ## Run the main application
	@echo "Running the application..."
	uv run python -m real_estate_agent.chat_agent

test: ## Run tests
	@echo "Running tests..."
	uv run pytest

test-azure: ## Test Azure OpenAI integration
	@echo "Testing Azure OpenAI integration..."
	uv run python test_azure_openai.py

lint: ## Run linting
	@echo "Running linting..."
	uv run ruff check .

format: ## Format code
	@echo "Formatting code..."
	uv run ruff format .

# Cleanup
clean: ## Clean Python cache files
	@echo "Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

clean-all: clean ## Clean everything including virtual environment
	@echo "Cleaning virtual environment..."
	uv venv remove --force 2>/dev/null || true
	@echo "All cleaned!"

# Migration from Poetry
migrate-from-poetry: ## Migrate from Poetry to uv
	@echo "Migrating from Poetry to uv..."
	@echo "1. Installing uv if not already installed..."
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Please install it first: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	@echo "2. Creating new virtual environment..."
	uv venv
	@echo "3. Installing dependencies from pyproject.toml..."
	uv sync
	@echo "4. Migration complete! You can now remove poetry.lock if desired."
	@echo "   Run 'make help' to see available commands."

# Utility commands
shell: ## Activate virtual environment shell
	@echo "Activating virtual environment..."
	uv shell

outdated: ## Show outdated packages
	@echo "Checking for outdated packages..."
	uv pip list --outdated

tree: ## Show dependency tree
	@echo "Showing dependency tree..."
	uv tree

# Environment setup
setup-env: ## Setup development environment
	@echo "Setting up development environment..."
	uv venv
	uv sync
	@echo "Development environment ready!"

# Quick development workflow
dev: install-dev ## Install dev dependencies and run in development mode
	@echo "Development environment ready!"
	@echo "Run 'make run' to start the application"

# Docker-like commands for consistency
build: install ## Build the project (alias for install)
	@echo "Project built successfully!"

start: run ## Start the application (alias for run)

stop: ## Stop the application (placeholder for future use)
	@echo "Application stopped."

restart: stop start ## Restart the application

# Database setup
setup-db: ## Setup MongoDB database
	@echo "Setting up MongoDB database..."
	uv run python setup_mongodb.py

# Logging setup
setup-logging: ## Setup logging configuration
	@echo "Setting up logging configuration..."
	@if [ -f "logging_config.py" ]; then \
		echo "Logging configuration file found."; \
	else \
		echo "Warning: logging_config.py not found."; \
	fi 