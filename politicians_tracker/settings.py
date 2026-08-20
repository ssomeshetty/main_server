"""
Django settings for Karnataka Politicians Tracker.

This is a comprehensive settings file optimized for high-performance,
read-only public API with bilingual support.
"""
from pathlib import Path
import os
import sys

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# CORE SECURITY SETTINGS
# =============================================================================
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

# SECRET_KEY — MUST be set via environment in production
_secret_key = os.environ.get('DJANGO_SECRET_KEY', '')
if not _secret_key and not DEBUG:
    raise RuntimeError(
        'DJANGO_SECRET_KEY environment variable is required in production. '
        'Generate one with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"'
    )
SECRET_KEY = _secret_key or 'dev-only-insecure-key-do-not-use-in-production'

# ALLOWED_HOSTS — env var + known production domains
_env_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
_env_host_list = [h.strip() for h in _env_hosts.split(',') if h.strip()] if _env_hosts else []
ALLOWED_HOSTS = list(set(_env_host_list + [
    'localhost',
    '127.0.0.1',
    'api.karnatakapoliticians.in',
    'www.karnatakapoliticians.in',
    'karnatakapoliticians.vercel.app',
]))

# CSRF trusted origins (required since Django 4.0 for HTTPS)
CSRF_TRUSTED_ORIGINS = [
    'https://api.karnatakapoliticians.in',
    'https://www.karnatakapoliticians.in',
    'https://karnatakapoliticians.vercel.app',
]

# Security middleware settings
SECURE_BROWSER_XSS_FILTER = True  # Enable XSS protection header
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking via iframes
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
SECURE_HSTS_SECONDS = 31536000  # HTTP Strict Transport Security (1 year)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# SSL/TLS settings (for production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie settings
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Content Security Policy (CSP)
CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'"]
CSP_STYLE_SRC = ["'self'"]
CSP_IMG_SRC = ["'self'", 'data:', 'https:']
CSP_FONT_SRC = ["'self'"]
CSP_CONNECT_SRC = ["'self'"]
CSP_FRAME_ANCESTORS = ["'none'"]  # Prevent framing

# Application definition
INSTALLED_APPS = [
    # Django defaults
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'django_filters',
    'corsheaders',  # CORS support
    
    # Local apps
    'politicians_tracker.apps.core',
]

MIDDLEWARE = [
    # Security middleware (order matters — SecurityMiddleware first)
    'django.middleware.security.SecurityMiddleware',

    # WhiteNoise for efficient static file serving (immediately after SecurityMiddleware)
    'whitenoise.middleware.WhiteNoiseMiddleware',

    # Request sanitization and size limiting (before any processing)
    'politicians_tracker.apps.core.middleware.RequestSanitizationMiddleware',
    'politicians_tracker.apps.core.middleware.RequestSizeLimitMiddleware',

    # GZip compression (~70% bandwidth savings for JSON responses)
    'django.middleware.gzip.GZipMiddleware',

    # CORS before CommonMiddleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',

    # Session + Auth (required for admin panel — minimal overhead for API)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    # Locale for bilingual support
    'django.middleware.locale.LocaleMiddleware',

    # Read-only enforcement (after auth so admin bypasses this)
    'politicians_tracker.apps.core.middleware.ReadOnlyModeMiddleware',

    # Language detection for bilingual API
    'politicians_tracker.apps.core.middleware.LanguageDetectionMiddleware',

    # Security response headers (last — adds headers to all responses)
    'politicians_tracker.apps.core.middleware.SecurityHeadersMiddleware',
]

ROOT_URLCONF = 'politicians_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'politicians_tracker.wsgi.application'

# =============================================================================
# CORS CONFIGURATION
# =============================================================================
# Allow only your Next.js frontend domain
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Next.js local development
    'http://127.0.0.1:3000',
    'https://karnatakapoliticians.vercel.app',  # Vercel production
]

# Restrict methods to safe read-only methods only
CORS_ALLOW_METHODS = [
    'GET',
    'HEAD',
    'OPTIONS',
]

# Restrict headers to safe headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'accept-language',
    'lang',
]

# Disable credentials for public API
CORS_ALLOW_CREDENTIALS = False

# CORS re-expose headers
CORS_EXPOSE_HEADERS = [
    'content-range',
    'x-total-count',
]

# Long cache for CORS preflight
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# Regex patterns for Vercel branch previews (escaped properly)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^https://karnatakapoliticians-git-[a-zA-Z0-9_-]+\.vercel\.app$',
]

# =============================================================================
# Database
# =============================================================================
# USE_SQLITE=true for local dev only; production defaults to MySQL
if os.environ.get('USE_SQLITE', 'false').lower() == 'true':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQL_DATABASE', 'politicians_tracker'),
            'USER': os.environ.get('MYSQL_USER', 'politicians_user'),
            'PASSWORD': os.environ.get('MYSQL_PASSWORD', ''),
            'HOST': os.environ.get('MYSQL_HOST', 'localhost'),
            'PORT': os.environ.get('MYSQL_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',  # Full Unicode support including Kannada
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

# Connection pooling — persistent in production, short-lived in dev
if not DEBUG:
    DATABASES['default']['CONN_MAX_AGE'] = 300  # 5 minutes
else:
    DATABASES['default']['CONN_MAX_AGE'] = 60

# =============================================================================
# Password validation (minimal for read-only public site)
# =============================================================================
AUTH_PASSWORD_VALIDATORS = []

# =============================================================================
# Internationalization
# =============================================================================
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Languages
LANGUAGES = [
    ('en', 'English'),
    ('kn', 'ಕನ್ನಡ'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# WhiteNoise compressed static files for production
if not DEBUG:
    STORAGES = {
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# REDIS CACHING CONFIGURATION
# =============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            # Connection pool settings
            'MAX_CONNECTIONS': 100,
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            # Socket timeout
            'SOCKET_TIMEOUT': 5,
            'SOCKET_CONNECT_TIMEOUT': 5,
            # Password (if Redis requires auth)
            'PASSWORD': os.environ.get('REDIS_PASSWORD', None),
            # Database number
            'DB': 1,
        },
        # Key prefix for namespace isolation
        'KEY_PREFIX': 'politicians',
        # Default timeout
        'TIMEOUT': 300,  # 5 minutes default
    },
    # Separate cache for sessions
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/2'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'DB': 2,
        },
        'KEY_PREFIX': 'session',
    },
}

# Session engine using Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'

# Cache key patterns
CACHE_KEY_PREFIX = 'politicians_api'

# Cache timeout presets (in seconds) — tuned for read-only data
CACHE_TTL_SHORT = 120        # 2 minutes — for frequently changing data
CACHE_TTL_MEDIUM = 600       # 10 minutes — for list views
CACHE_TTL_LONG = 1800        # 30 minutes — for detail views
CACHE_TTL_VERY_LONG = 7200   # 2 hours — for static reference data (districts, parties)
CACHE_TTL_ANALYTICS = 1800   # 30 minutes — for analytics aggregations

# =============================================================================
# DJANGO REST FRAMEWORK CONFIGURATION
# =============================================================================
REST_FRAMEWORK = {
    # ==========================================================================
    # AGGRESSIVE RATE LIMITING (per-endpoint scopes)
    # ==========================================================================
    # Throttle classes for anonymous users
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],

    # Rate limits per throttle scope
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',           # Global fallback: 60 req/min per IP
        'burst_anon': '100/minute',    # Burst limit
        'analytics': '10/minute',      # Analytics is expensive — strict limit
        'list': '60/minute',           # List endpoints
        'detail': '120/minute',        # Detail endpoints (lighter)
        'search': '30/minute',         # Search is DB-heavy
    },
    
    # Authentication (none required for read-only public API)
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    
    # Permissions - AllowAny for public data
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    
    # ==========================================================================
    # PAGINATION & RENDERING
    # ==========================================================================
    'DEFAULT_PAGINATION_CLASS': 'politicians_tracker.apps.core.pagination.CustomCursorPagination',
    'PAGE_SIZE': 20,
    
    # Rendering
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    
    # ==========================================================================
    # FILTERING
    # ==========================================================================
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # ==========================================================================
    # CACHING (DRF cache responses)
    # ==========================================================================
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': CACHE_TTL_LONG,  # 15 minutes
    
    # ==========================================================================
    # EXCEPTION HANDLING
    # ==========================================================================
    'EXCEPTION_HANDLER': 'politicians_tracker.apps.core.exceptions.custom_exception_handler',
}

# =============================================================================
# RATE LIMITING CUSTOM CLASSES
# =============================================================================
# Custom throttling for more granular control
THROTTLE_CLASSES = {
    'default': {
        'scope': 'anon',
        'rate': '60/minute',
    },
    'burst': {
        'scope': 'burst_anon',
        'rate': '100/minute',
    },
}

# =============================================================================
# DATABASE OPTIMIZATION
# =============================================================================
# Enable query caching
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB max upload

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        # Log throttling events
        'rest_framework.throttling': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'politicians_tracker': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Production file-based logging (logs survive container restarts)
if not DEBUG:
    _log_dir = BASE_DIR / 'logs'
    _log_dir.mkdir(exist_ok=True)
    LOGGING['handlers']['file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': _log_dir / 'django.log',
        'maxBytes': 10 * 1024 * 1024,  # 10MB
        'backupCount': 5,
        'formatter': 'verbose',
    }
    LOGGING['loggers']['django.request']['handlers'] = ['console', 'file']
    LOGGING['loggers']['politicians_tracker']['handlers'] = ['console', 'file']

# =============================================================================
# LLM API CONFIGURATION (for LLM purification worker)
# =============================================================================
LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'google')
LLM_MODEL = os.environ.get('LLM_MODEL', 'gemini-2.0-flash-exp')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# LLM worker settings
LLM_WORKER_BATCH_SIZE = int(os.environ.get('LLM_WORKER_BATCH_SIZE', 10))
LLM_WORKER_MAX_RETRIES = int(os.environ.get('LLM_WORKER_MAX_RETRIES', 3))
LLM_WORKER_CONCURRENCY = int(os.environ.get('LLM_WORKER_CONCURRENCY', 4))

# =============================================================================
# PRODUCTION OVERRIDES
# =============================================================================
if not DEBUG:
    # Cache - longer in production
    CACHE_TTL_LONG = 1800  # 30 minutes

    # Logging
    LOGGING['loggers']['politicians_tracker']['level'] = 'INFO'

    # Rate limiting - robust limits for production frontend browsing
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon'] = '500/minute'
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['burst_anon'] = '1000/minute'
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['analytics'] = '60/minute'
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['search'] = '300/minute'
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['list'] = '1000/minute'

if 'test' in sys.argv:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []