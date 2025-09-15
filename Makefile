# Dynamic Stress Testing Framework - Simplified Makefile

.PHONY: help demo test setup clean

# Default target
help:
	@echo "Dynamic Stress Testing Framework"
	@echo "================================"
	@echo ""
	@echo "Basic Commands:"
	@echo "  make demo     - Quick demo (Swagger Petstore)"
	@echo "  make test     - Run framework tests"
	@echo "  make setup    - Copy example config"
	@echo "  make clean    - Clean up everything"
	@echo ""
	@echo "Development:"
	@echo "  make mock     - Start local mock server"
	@echo "  make health   - Check system health"
	@echo ""
	@echo "Usage:"
	@echo "  1. make setup"
	@echo "  2. Edit .env file"
	@echo "  3. make demo"

# Quick demo - works out of the box
demo:
	@echo "Starting demo..."
	@cp examples/.env.petstore .env 2>/dev/null || true
	@docker compose up --build

# Run tests
test:
	@echo "Running tests..."
	@docker compose build
	@docker compose run --rm locust python3 test_framework.py --comprehensive

# Setup config file
setup:
	@echo "Setting up..."
	@cp examples/.env.petstore .env
	@echo "Config copied to .env - edit it with your API details"
	@echo "Then run: make demo"

# Clean everything
clean:
	@echo "Cleaning up..."
	@docker compose down -v
	@docker system prune -f
	@rm -rf reports/* 2>/dev/null || true

# Start mock server for development
mock:
	@echo "Starting mock server at http://localhost:5000"
	@cp examples/.env.mock_server .env 2>/dev/null || true
	@docker compose -f compose.mock.yaml up --build

# Quick health check
health:
	@echo "Health check..."
	@docker compose run --rm locust python3 scenarios/troubleshoot.py --quick

# Build only (no run)
build:
	@docker compose build

# Show logs
logs:
	@docker compose logs -f