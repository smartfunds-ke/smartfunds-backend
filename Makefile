.PHONY: help dev prod build-dev build-prod up-dev up-prod down-dev down-prod down logs shell test clean migrate migrate-prod collectstatic createsuperuser
	

# Common commands
down:
	docker compose -f docker-compose.dev.yml down || true
	docker compose -f docker-compose.prod.yml down || true

logs:
	@if [ -z "$(ARGS)" ]; then \
		docker compose -f docker-compose.dev.yml logs -f; \
	else \
		docker compose -f docker-compose.dev.yml logs -f $(ARGS); \
	fi

shell:
	docker compose -f docker-compose.dev.yml exec web python manage.py shell

test:
	docker-compose -f docker-compose.dev.yml exec web python manage.py test

# Database commands
migrate:
	@echo "Running migrations in development..."
	docker-compose -f docker-compose.dev.yml exec web python manage.py migrate

migrate-prod:
	@echo "Running migrations in production..."
	docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

collectstatic:
	docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

createsuperuser:
	docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser

# Utility commands
clean:
	@echo "Stopping all containers..."
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans || true
	docker-compose -f docker-compose.prod.yml down -v --remove-orphans || true
	@echo "Removing unused images..."
	docker image prune -f
	@echo "Removing unused volumes..."
	docker volume prune -f

clean-all: clean
	@echo "Removing all project images..."
	docker images | grep smartfunds | awk '{print $3}' | xargs docker rmi -f || true

# Development tools
dev-tools:
	docker-compose -f docker-compose.dev.yml --profile dev-tools up -d mailhog adminer

monitoring:
	docker-compose -f docker-compose.prod.yml --profile monitoring up -d prometheus

# Backup and restore
backup-db:
	@echo "Creating database backup..."
	docker-compose -f docker-compose.prod.yml exec db pg_dump -U $(DATABASE_USER) $(DATABASE_NAME) > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make restore-db FILE=backup_file.sql"; \
	else \
		docker-compose -f docker-compose.dev.yml exec -T db psql -U $(DATABASE_USER) $(DATABASE_NAME) < $(FILE); \
	fi

# Security scan
security-scan:
	docker run --rm -v $(PWD):/app securecodewarrior/docker-security-scan /app

# Performance testing
load-test:
	docker-compose -f docker-compose.dev.yml exec web locust -f tests/locustfile.py --host=http://web:8000d down logs shell test clean

# Default target
help:
	@echo "Available commands:"
	@echo "  dev           - Start development environment"
	@echo "  prod          - Start production environment"
	@echo "  build-dev     - Build development images"
	@echo "  build-prod    - Build production images"
	@echo "  up-dev        - Start dev services (without build)"
	@echo "  up-prod       - Start prod services (without build)"
	@echo "  down-dev      - Stop development services"
	@echo "  down-prod     - Stop production services"
	@echo "  down          - Stop all services"
	@echo "  logs          - Show logs (use ARGS='service-name' for specific service)"
	@echo "  shell         - Access Django shell in development"
	@echo "  test          - Run tests in development environment"
	@echo "  clean         - Remove all containers, volumes, and images"
	@echo "  migrate       - Run database migrations"
	@echo "  collectstatic - Collect static files"
	@echo "  createsuperuser - Create Django superuser"

# Development commands
dev: build-dev up-dev down-dev

build-dev:
	docker compose -f docker-compose.dev.yml build

up-dev:
	docker compose -f docker-compose.dev.yml up

down-dev:
	docker compose -f docker-compose.dev.yml down || true

# Production commands
prod: build-prod up-prod

build-prod:
	docker compose -f docker-compose.prod.yml build

up-prod:
	docker compose -f docker-compose.prod.yml up -d
