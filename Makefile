# Dermalens — developer task runner.
# NOTE: requires GNU Make. On Windows, run these via WSL or Git Bash
# (or use the underlying npm / pytest commands directly in PowerShell).

.DEFAULT_GOAL := help
.PHONY: help install run run-backend test test-coverage lint format docker-build docker-run clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install frontend + backend dependencies
	npm install
	pip install -r apps/api/requirements.txt -r requirements-dev.txt

run: ## Run the frontend dev server (http://localhost:3000)
	npm run dev

run-backend: ## Run the backend API (http://localhost:8000)
	cd apps/api && uvicorn main:app --reload

test: ## Run all tests (frontend + backend)
	npm test
	pytest apps/api/tests

test-coverage: ## Run all tests with coverage
	npm run test:coverage
	pytest apps/api/tests --cov=apps/api --cov-report=term-missing

lint: ## Lint frontend + backend
	npm run lint
	black --check apps/api
	isort --check-only apps/api
	flake8 apps/api --count --select=E9,F63,F7,F82 --show-source --statistics

format: ## Auto-format frontend + backend
	npm run format
	black apps/api
	isort apps/api

docker-build: ## Build the frontend Docker image
	docker build -t dermalens-frontend .

docker-run: ## Start all services via docker compose
	docker compose up

clean: ## Remove build artifacts and caches
	rm -rf .next coverage node_modules/.cache .pytest_cache apps/api/.pytest_cache
	find . -type d -name __pycache__ -not -path "./node_modules/*" -prune -exec rm -rf {} + 2>/dev/null || true
