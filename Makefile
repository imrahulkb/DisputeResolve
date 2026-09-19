	.PHONY: help install dev test test-watch test-cov lint format clean docker-up docker-down

help:
	@echo "BillResolve — Billing Dispute Resolution Engine"
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "  make install       Install Python dependencies"
	@echo "  make dev           Run FastAPI server in development mode"
	@echo "  make test          Run all tests"
	@echo "  make test-watch    Run tests in watch mode (auto-reload on file change)"
	@echo "  make test-cov      Run tests with coverage report"
	@echo "  make lint          Run flake8 linter"
	@echo "  make format        Format code with black"
	@echo "  make clean         Remove pycache and build artifacts"
	@echo "  make docker-up     Start Docker services (PostgreSQL, Redis, ChromaDB)"
	@echo "  make docker-down   Stop Docker services"
	@echo ""

install:
	pip install -r requirements.txt

dev:
	uvicorn src.app:app --reload --port 8000

test:
	pytest src/tests/ -v

test-watch:
	ptw src/tests/ -- -v

test-cov:
	pytest src/tests/ --cov=src --cov-report=html -v
	@echo "Coverage report generated: htmlcov/index.html"

lint:
	flake8 src/ --count --show-source --statistics

format:
	black src/ --line-length 100

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov/
	rm -rf .coverage

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
