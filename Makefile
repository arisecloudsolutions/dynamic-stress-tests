# Dynamic Stress Testing Framework - Enhanced Makefile

.PHONY: help demo test setup clean validate dev-test

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
	@echo "  make validate - Validate configuration"
	@echo ""
	@echo "Development:"
	@echo "  make mock     - Start local mock server"
	@echo "  make health   - Check system health"
	@echo "  make dev-test - Run Python tests locally"
	@echo "  make analyze  - Analyze OpenAPI spec"
	@echo ""
	@echo "Usage:"
	@echo "  1. make setup"
	@echo "  2. Edit .env file"
	@echo "  3. make validate"
	@echo "  4. make demo"

# Quick demo - works out of the box
demo:
	@echo "Starting demo..."
	@cp examples/.env.petstore .env 2>/dev/null || true
	@docker compose up --build

# Run tests
test:
	@echo "Running framework tests..."
	@docker compose build
	@docker compose run --rm locust python3 src/test_framework.py --comprehensive

# Validate configuration
validate:
	@echo "Validating configuration..."
	@docker compose run --rm locust python3 src/config_validator.py

# Run Python tests locally (development)
dev-test:
	@echo "Running Python tests..."
	@python3 -m pytest tests/ -v

# Analyze OpenAPI specification
analyze:
	@echo "Analyzing OpenAPI specification..."
	@docker compose run --rm locust python3 src/endpoint_visualizer.py

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
	@docker compose run --rm locust python3 src/config_validator.py --health

# Build only (no run)
build:
	@docker compose build

# Show logs
logs:
	@docker compose logs -f