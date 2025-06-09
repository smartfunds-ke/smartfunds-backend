#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Wait for database
if [ "$DATABASE" = "postgres" ] || [ "$DATABASE_ENGINE" = "django.db.backends.postgresql" ]; then
    log_info "Waiting for PostgreSQL..."
    
    # Default values if not set
    DB_HOST=${DATABASE_HOST:-db}
    DB_PORT=${DATABASE_PORT:-5432}
    
    while ! nc -z "$DB_HOST" "$DB_PORT"; do
        log_warn "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    
    log_info "PostgreSQL is up - executing command"
fi

# Wait for Redis if using Celery
if [ "$USE_CELERY" = "true" ] || [ "$CELERY_BROKER_URL" ]; then
    log_info "Waiting for Redis..."
    
    REDIS_HOST=${REDIS_HOST:-redis}
    REDIS_PORT=${REDIS_PORT:-6379}
    
    while ! nc -z "$REDIS_HOST" "$REDIS_PORT"; do
        log_warn "Redis is unavailable - sleeping"
        sleep 1
    done
    
    log_info "Redis is up"
fi

# Run database migrations (only for web service)
if [ "$1" = "gunicorn" ] || [ "$1" = "python" ] && [ "$2" = "manage.py" ] && [ "$3" = "runserver" ]; then
    log_info "Running database migrations..."
    python manage.py migrate --noinput || {
        log_error "Migration failed"
        exit 1
    }
    
    # Collect static files in production
    if [ "$DJANGO_SETTINGS_MODULE" != *"development"* ]; then
        log_info "Collecting static files..."
        python manage.py collectstatic --noinput --clear || {
            log_warn "Static files collection failed, continuing..."
        }
    fi
    
    # Create superuser if specified
    if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
        log_info "Creating superuser..."
        python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser(username='$DJANGO_SUPERUSER_USERNAME', email='$DJANGO_SUPERUSER_EMAIL', password='$DJANGO_SUPERUSER_PASSWORD', first_name='$DJANGO_SUPERUSER_FIRST_NAME', last_name='$DJANGO_SUPERUSER_LAST_NAME', phone_number='$DJANGO_SUPERUSER_PHONE_NUMBER')
    print('Superuser created')
else:
    print('Superuser already exists')
EOF
    fi
fi

# Execute the main command
log_info "Executing command: $*"
exec "$@"