# Makefile for Karnataka Politicians Tracker Core App

.PHONY: help test lint migrate freeze-requirements

help:
	@echo "Karnataka Politicians Tracker - Makefile Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  test          Run all tests with coverage"
	@echo "  test-verbose  Run tests with verbose output"
	@echo "  lint          Run linting checks"
	@echo "  migrate       Run database migrations"
	@echo "  migrate-dev   Create and run migrations for development"
	@echo "  freeze        Freeze dependencies to requirements.txt"
	@echo "  clean         Clean up temporary files"
	@echo "  docker-up     Start Docker services"
	@echo "  docker-down   Stop Docker services"

test:
	@echo "Running tests with coverage..."
	python -m coverage run manage.py test politicians_tracker.apps.core --verbosity=2
	python -m coverage report
	python -m coverage html

test-verbose:
	@echo "Running tests with verbose output..."
	python manage.py test politicians_tracker.apps.core --verbosity=2

lint:
	@echo "Running linting checks..."
	# Uncomment and configure if using flake8 or pylint
	# flake8 politicians_tracker/apps/core --max-line-length=120
	# pylint politicians_tracker/apps/core

migrate:
	@echo "Running database migrations..."
	python manage.py migrate

migrate-dev:
	@echo "Creating and running migrations..."
	python manage.py makemigrations
	python manage.py migrate

freeze:
	@echo "Freezing dependencies..."
	pip freeze > requirements.txt

clean:
	@echo "Cleaning up temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov .tox .pytest_cache
	rm -rf politicians_tracker/apps/core/migrations/00*.py
	find politicians_tracker/apps/core/migrations -name "00*.py" ! -name "0001_initial.py" -delete
	@echo "Cleanup complete!"

docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

# Test specific components
test-api:
	@echo "Running API endpoint tests..."
	python manage.py test politicians_tracker.apps.core.tests.test_api_endpoints

test-serializers:
	@echo "Running serializer tests..."
	python manage.py test politicians_tracker.apps.core.tests.test_serializers

test-models:
	@echo "Running model tests..."
	python manage.py test politicians_tracker.apps.core.tests.test_models

# Performance tests
test-performance:
	@echo "Running performance tests..."
	python manage.py test politicians_tracker.apps.core.tests.test_performance

# Database operations
db-reset:
	@echo "Resetting database..."
	python manage.py flush --no-input
	python manage.py migrate

db-migrate-dev:
	@echo "Creating migrations for development..."
	python manage.py makemigrations politicians_tracker.apps.core
	python manage.py migrate politicians_tracker.apps.core

# Data operations
load-data:
	@echo "Loading initial data..."
	python manage.py loaddata districts.json
	python manage.py loaddata parties.json

dump-data:
	@echo "Dumping data..."
	python manage.py dumpdata core.District > districts.json
	python manage.py dumpdata core.Party > parties.json
