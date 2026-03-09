.PHONY: help install setup start stop restart status logs clean test migrate seed db-test lint format ruff-check ruff-fix ruff-format

# Default target
help:
	@echo "Legacy Migration Tool - Available Commands"
	@echo "=========================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          - Install dependencies with UV"
	@echo "  make setup            - Complete setup (install + start databases)"
	@echo ""
	@echo "Docker Management:"
	@echo "  make start            - Start Docker containers"
	@echo "  make stop             - Stop Docker containers"
	@echo "  make restart          - Restart Docker containers"
	@echo "  make status           - Show container status"
	@echo "  make logs             - Show container logs"
	@echo "  make clean            - Stop and remove containers, volumes, networks"
	@echo ""
	@echo "Database Operations:"
	@echo "  make db-test          - Test database connections"
	@echo "  make db-status        - Show database status"
	@echo "  make db-create        - Create database tables"
	@echo ""
	@echo "Data Seeding:"
	@echo "  make seed-ben         - Seed 3000 beneficiaries"
	@echo "  make seed-dep         - Seed 2000 dependents"
	@echo "  make seed-all         - Seed all data"
	@echo ""
	@echo "Migration:"
	@echo "  make migrate-ben      - Migrate beneficiaries"
	@echo "  make migrate-dep      - Migrate dependents"
	@echo "  make migrate-all      - Migrate all data"
	@echo "  make dry-run          - Test migration (dry run)"
	@echo ""
	@echo "Development:"
	@echo "  make test             - Run tests"
	@echo "  make lint             - Run all linting (ruff check)"
	@echo "  make format           - Format code with ruff"
	@echo "  make ruff-check       - Check code with ruff (no fixes)"
	@echo "  make ruff-fix         - Fix auto-fixable ruff issues"
	@echo "  make ruff-format      - Format code with ruff"
	@echo "  make ruff-format-check - Check if code is formatted"
	@echo "  make show-config      - Show current configuration"
	@echo ""
	@echo "Examples:"
	@echo "  make setup            - First time setup"
	@echo "  make seed-all         - Generate test data"
	@echo "  make dry-run          - Test migration"
	@echo "  make migrate-all      - Run full migration"

# Installation
install:
	@echo "Installing dependencies with UV..."
	uv sync

# Complete setup
setup: install
	@echo "Creating .env from .env.example..."
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo "Waiting for databases to initialize (30 seconds)..."
	@sleep 30
	@echo "Testing database connections..."
	uv run python main.py db test
	@echo ""
	@echo "✓ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Seed test data: make seed-all"
	@echo "  2. Run migration: make migrate-all"

# Docker commands
start:
	@echo "Starting Docker containers..."
	docker-compose up -d

stop:
	@echo "Stopping Docker containers..."
	docker-compose stop

restart:
	@echo "Restarting Docker containers..."
	docker-compose restart

status:
	@echo "Container status:"
	docker-compose ps

logs:
	@echo "Showing logs (Ctrl+C to exit)..."
	docker-compose logs -f

clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down -v
	@echo "Removing log files..."
	rm -rf logs/
	@echo "✓ Cleanup complete!"

# Database operations
db-test:
	@echo "Testing database connections..."
	uv run python main.py db test

db-status:
	@echo "Checking database status..."
	uv run python main.py db status

db-create:
	@echo "Creating database tables..."
	uv run python main.py db create-tables

# Seeding
seed-ben:
	@echo "Seeding 3000 beneficiaries..."
	uv run python main.py seed beneficiary --count 3000

seed-dep:
	@echo "Seeding 2000 dependents..."
	uv run python main.py seed dependent --count 2000

seed-all: seed-ben seed-dep
	@echo "✓ All seeding complete!"

# Migration
migrate-ben:
	@echo "Migrating beneficiaries..."
	uv run python main.py migrate beneficiary

migrate-dep:
	@echo "Migrating dependents..."
	uv run python main.py migrate dependent

migrate-all:
	@echo "Migrating all data..."
	uv run python main.py migrate all

dry-run:
	@echo "Running migration in DRY RUN mode..."
	uv run python main.py --dry-run migrate all

# Development
test:
	@echo "Running tests..."
	uv run pytest tests/ -v

# Ruff linting and formatting
ruff-check:
	@echo "Checking code with ruff..."
	uv run ruff check .

ruff-fix:
	@echo "Fixing auto-fixable issues with ruff..."
	uv run ruff check --fix .

lint: ruff-check
	@echo "✓ Linting complete!"

ruff-format:
	@echo "Formatting code with ruff..."
	uv run ruff format .

ruff-format-check:
	@echo "Checking code formatting..."
	uv run ruff format --check .

format: ruff-format
	@echo "✓ Formatting complete!"

# Run all checks
check: ruff-format-check ruff-check
	@echo "✓ All checks passed!"

show-config:
	@echo "Current configuration:"
	uv run python main.py config

# Complete workflow
workflow: setup seed-all dry-run migrate-all
	@echo ""
	@echo "✓ Complete workflow finished!"
	@echo ""
	@make db-status