"""
Development settings for smartfunds project.
"""

import warnings
from .base import *
import os


DEBUG = True

# Allowed hosts for development
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'web',
    'host.docker.internal',
]

# Database - Override with development-specific settings
DATABASES['default'].update({
    'OPTIONS': {
        'sslmode': 'disable',
    }
})

# Add development-specific apps
INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
    'silk',
]

# Add development middleware
MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'silk.middleware.SilkyMiddleware',
] + MIDDLEWARE

# Debug Toolbar Configuration
INTERNAL_IPS = [
    '127.0.0.1',
    '0.0.0.0',
    'localhost',
]

# For Docker development
if os.environ.get('USE_DOCKER') == 'yes':
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [
        ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}

# Django Silk Configuration (Performance Profiling)
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True
SILKY_AUTHENTICATION = True
SILKY_AUTHORISATION = True
SILKY_META = True
SILKY_INTERCEPT_PERCENT = 100  # Profile all requests in development

# Email Configuration for Development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Uncomment below to use MailHog
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'mailhog'
# EMAIL_PORT = 1025
# EMAIL_USE_TLS = False

# CORS Configuration for Development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# CSRF Configuration for Development
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Cache Configuration - Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'smartfunds_dev',
    }
}

# Session Configuration for Development
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400 * 7  # 7 days for development convenience

# Security Settings for Development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Django Extensions Configuration
SHELL_PLUS_PRINT_SQL = True
SHELL_PLUS_PRINT_SQL_TRUNCATE = None

# REST Framework Configuration for Development
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/hour',
        'user': '10000/hour',
        'login': '50/min',
        'signup': '30/min',
    }
})

# Celery Configuration for Development
CELERY_TASK_ALWAYS_EAGER = False  # Set to True to run tasks synchronously
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_WORKER_CONCURRENCY = 1
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# File Upload Configuration for Development
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB

# Static Files Configuration for Development
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Development-specific logging
LOGGING.update({
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'development.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'smartfunds': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # 'django.db.backends': {
        #     'handlers': ['console'],
        #     'level': 'DEBUG',
        #     'propagate': False,
        # },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
})

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Django Debug Toolbar Panels
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.history.HistoryPanel',
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

# API Documentation - Include schema in development
SPECTACULAR_SETTINGS.update({
    'SERVE_INCLUDE_SCHEMA': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'displayOperationId': True,
        'defaultModelsExpandDepth': 2,
        'defaultModelExpandDepth': 2,
        'displayRequestDuration': True,
        'filter': True,
    },
})

# Development-specific settings
DEVELOPMENT_SETTINGS = {
    'AUTO_RELOAD': True,
    'SHOW_TOOLBAR': True,
    'PROFILE_REQUESTS': True,
    'LOG_SQL_QUERIES': True,
}

# Disable security warnings in development
warnings.filterwarnings('ignore', message='You have.*unapplied migration')

print("🚀 Development settings loaded!")
print(f"📊 Debug Toolbar: {'Enabled' if DEBUG else 'Disabled'}")
print(f"📧 Email Backend: {EMAIL_BACKEND}")
print(f"🗄️ Cache Backend: {CACHES['default']['BACKEND']}")
print(f"⚡ Celery Eager: {CELERY_TASK_ALWAYS_EAGER}")
print(
    f"🔍 SQL Logging: {'Enabled' if 'django.db.backends' in LOGGING['loggers'] else 'Disabled'}")
print(f"📦 Installed Apps: {INSTALLED_APPS}")
