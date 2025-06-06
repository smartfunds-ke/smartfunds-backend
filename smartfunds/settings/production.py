"""
Production settings for smartfunds_backend project.
"""

from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
import os

DEBUG = False

# Allowed hosts for production
ALLOWED_HOSTS = [
    host.strip() for host in get_env_variable('ALLOWED_HOSTS', '').split(',') if host.strip()
]

# Security Configuration
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https:")

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in get_env_variable('CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()
]

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in get_env_variable('CORS_ALLOWED_ORIGINS', '').split(',') if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True

# Database Configuration with SSL
DATABASES['default'].update({
    'CONN_MAX_AGE': 600,
    'CONN_HEALTH_CHECKS': True,
    'OPTIONS': {
        'sslmode': 'require',
        'connect_timeout': 10,
        'options': '-c default_transaction_isolation=serializable'
    },
})

# Add production-specific apps
INSTALLED_APPS += [
    # 'django_prometheus',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
]

# Add production middleware
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
] + MIDDLEWARE + [
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# Static Files Configuration with WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = [
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br']

# Media Files Configuration (Consider using S3 in production)
# AWS S3 Configuration (uncomment if using S3)
# AWS_ACCESS_KEY_ID = get_env_variable('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = get_env_variable('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = get_env_variable('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = get_env_variable('AWS_S3_REGION_NAME', 'us-east-1')
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
# AWS_DEFAULT_ACL = 'public-read'
# AWS_S3_OBJECT_PARAMETERS = {
#     'CacheControl': 'max-age=86400',
# }
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

# Cache Configuration with Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'smartfunds_prod',
        'TIMEOUT': 300,
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1800  # 30 minutes
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_SAVE_EVERY_REQUEST = True

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = get_env_variable('EMAIL_HOST')
EMAIL_PORT = int(get_env_variable('EMAIL_PORT', '587'))
EMAIL_USE_TLS = get_env_variable('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = get_env_variable(
    'DEFAULT_FROM_EMAIL', 'noreply@smartfunds.com')
SERVER_EMAIL = get_env_variable('SERVER_EMAIL', DEFAULT_FROM_EMAIL)
EMAIL_TIMEOUT = 10

# Celery Configuration for Production
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_WORKER_CONCURRENCY = int(
    get_env_variable('CELERY_WORKER_CONCURRENCY', '2'))
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_TASK_COMPRESSION = 'gzip'
CELERY_RESULT_COMPRESSION = 'gzip'
CELERY_TASK_ROUTES = {
    'apps.notifications.tasks.*': {'queue': 'notifications'},
    'apps.funds.tasks.*': {'queue': 'funds'},
    'apps.core.tasks.*': {'queue': 'default'},
}
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_CREATE_MISSING_QUEUES = True

# Celery Beat Configuration
CELERY_BEAT_SCHEDULE = {
    'health-check': {
        'task': 'apps.core.tasks.health_check',
        'schedule': 300.0,  # 5 minutes
    },
    'cleanup-expired-sessions': {
        'task': 'apps.core.tasks.cleanup_expired_sessions',
        'schedule': 3600.0,  # 1 hour
    },
}

# REST Framework Configuration for Production
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/min',
        'signup': '3/min',
        'password_reset': '3/hour',
    }
})

# File Upload Configuration
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024  # 2MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024  # 2MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 100

# Sentry Configuration for Error Tracking
SENTRY_DSN = get_env_variable('SENTRY_DSN', '')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
            ),
            CeleryIntegration(
                monitor_beat_tasks=True,
                propagate_traces=True,
            ),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=get_env_variable('ENVIRONMENT', 'production'),
        release=get_env_variable('APP_VERSION', '1.0.0'),
        before_send=lambda event, hint: event if event.get(
            'level') in ['error', 'fatal'] else None,
    )

# Logging Configuration for Production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "process": %(process)d, "thread": %(thread)d, "message": "%(message)s"}',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/production.log',
            'maxBytes': 1024 * 1024 * 100,  # 100MB
            'backupCount': 10,
            'formatter': 'json',
            'level': 'INFO',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/error.log',
            'maxBytes': 1024 * 1024 * 50,  # 50MB
            'backupCount': 5,
            'formatter': 'json',
            'level': 'ERROR',
        },
        'sentry': {
            'class': 'sentry_sdk.integrations.logging.SentryHandler',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['console', 'file', 'sentry'] if SENTRY_DSN else ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'error_file', 'sentry'] if SENTRY_DSN else ['console', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'error_file', 'sentry'] if SENTRY_DSN else ['console', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'smartfunds': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'gunicorn.error': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'gunicorn.access': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Health Check Configuration
HEALTH_CHECK_APPS = [
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
]

# Monitoring Configuration
PROMETHEUS_METRICS_EXPORT_PORT = int(
    get_env_variable('PROMETHEUS_METRICS_EXPORT_PORT', '8001'))
PROMETHEUS_METRICS_EXPORT_ADDRESS = get_env_variable(
    'PROMETHEUS_METRICS_EXPORT_ADDRESS', '')

# Performance Optimizations
# Database connection pooling
DATABASES['default']['OPTIONS'].update({
    'MAX_CONNS': 20,
    'MIN_CONNS': 5,
})

# Cache optimizations
CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_KEY_PREFIX = 'smartfunds_prod'

# API Documentation - Disable in production for security
SPECTACULAR_SETTINGS.update({
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'displayOperationId': False,
        'filter': False,
    },
})

# Production-specific settings
PRODUCTION_SETTINGS = {
    'ENVIRONMENT': 'production',
    'APP_NAME': APP_NAME,
    'APP_VERSION': APP_VERSION,
    'DEBUG': DEBUG,
    'SENTRY_ENABLED': bool(SENTRY_DSN),
    'PROMETHEUS_ENABLED': True,
    'HEALTH_CHECKS_ENABLED': True,
}

# Password validation - Enhanced for production
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Increased from 8 for production
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Additional security headers
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_TZ = True

# Rate limiting for production
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Disable browsable API in production
if 'rest_framework.renderers.BrowsableAPIRenderer' in REST_FRAMEWORK.get('DEFAULT_RENDERER_CLASSES', []):
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].remove(
        'rest_framework.renderers.BrowsableAPIRenderer')

# Additional middleware for production
MIDDLEWARE.insert(1, 'django.middleware.cache.UpdateCacheMiddleware')
MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')

# Create logs directory on container startup
os.makedirs('/app/logs', exist_ok=True)

print("🚀 Production settings loaded!")
print(
    f"🔒 Security: SSL Redirect {'Enabled' if SECURE_SSL_REDIRECT else 'Disabled'}")
print(f"📊 Sentry: {'Enabled' if SENTRY_DSN else 'Disabled'}")
print(f"🗄️ Cache: {CACHES['default']['BACKEND']}")
print(f"📧 Email Backend: {EMAIL_BACKEND}")
print(f"⚡ Celery Workers: {CELERY_WORKER_CONCURRENCY}")
print(f"🔍 Debug Mode: {DEBUG}")
