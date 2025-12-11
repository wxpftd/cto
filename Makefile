.PHONY: help install setup dev worker migrate migrate-create test clean docker-up docker-down docker-logs

help:
	@echo "Feedback Loop API - Available Commands"
	@echo "======================================"
	@echo "install          - Install dependencies"
	@echo "setup            - Setup environment and run migrations"
	@echo "dev              - Start development server"
	@echo "worker           - Start Celery worker"
	@echo "migrate          - Run database migrations"
	@echo "migrate-create   - Create new migration"
	@echo "test             - Run tests (TODO)"
	@echo "clean            - Clean temporary files"
	@echo "docker-up        - Start all services with Docker Compose"
	@echo "docker-down      - Stop all Docker services"
	@echo "docker-logs      - View Docker logs"
	@echo "docker-migrate   - Run migrations in Docker"
	@echo "docker-shell     - Open shell in API container"

install:
	pip install -r requirements.txt

setup:
	@echo "Setting up environment..."
	@test -f .env || cp .env.example .env
	@echo "Running migrations..."
	alembic upgrade head
	@echo "Initializing sample data..."
	python scripts/init_db.py
	@echo "Setup complete!"

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	celery -A app.workers.celery_app worker --loglevel=info

migrate:
	alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

test:
	@echo "Tests not yet implemented"
	# pytest tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

docker-up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "Services started! Running migrations..."
	docker-compose exec api alembic upgrade head
	@echo "Done! API: http://localhost:8000/docs"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-migrate:
	docker-compose exec api alembic upgrade head

docker-shell:
	docker-compose exec api /bin/bash
