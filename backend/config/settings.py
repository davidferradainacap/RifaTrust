"""
Django settings for RifaTrust.
"""

from pathlib import Path
from decouple import config as env_config
import os

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
PROJECT_ROOT = BASE_DIR.parent  # RS_project/

# Security Settings
SECRET_KEY = env_config('SECRET_KEY', default='django-insecure-cambiar-en-produccion')
DEBUG = env_config('DEBUG', default=True, cast=bool)
allowed_hosts_str = env_config('ALLOWED_HOSTS', default='')
ALLOWED_HOSTS = allowed_hosts_str.split(',') if allowed_hosts_str else ['*']

# CSRF Trusted Origins (para Azure y producción)
csrf_origins_str = env_config('CSRF_TRUSTED_ORIGINS', default='https://rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net')
CSRF_TRUSTED_ORIGINS = csrf_origins_str.split(',') if csrf_origins_str else []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'corsheaders',
    'django_filters',
    'crispy_forms',
    'crispy_bootstrap5',
    'axes',  # Rate limiting y protección contra fuerza bruta

    # Local apps
    'apps.users',
    'apps.raffles',
    'apps.payments',
    'apps.admin_panel',
]

# Custom User Model
AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',  # Rate limiting - debe ir después de AuthenticationMiddleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [PROJECT_ROOT / 'frontend' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Configuración flexible: SQLite por defecto, MySQL cuando esté disponible
DB_ENGINE = env_config('DATABASE_ENGINE', default='django.db.backends.sqlite3')

if DB_ENGINE == 'django.db.backends.sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': PROJECT_ROOT / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': env_config('DATABASE_NAME', default='RifaTrust'),
            'USER': env_config('DATABASE_USER', default='root'),
            'PASSWORD': env_config('DATABASE_PASSWORD', default=''),
            'HOST': env_config('DATABASE_HOST', default='localhost'),
            'PORT': env_config('DATABASE_PORT', default='3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'ssl': {'ssl-mode': 'required'}
            },
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Password Hashers - Usar Argon2 (más seguro que PBKDF2)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Encryption Key - Para campos sensibles
# IMPORTANTE: En producción, usar una clave diferente a SECRET_KEY
ENCRYPTION_KEY = env_config('ENCRYPTION_KEY', default=SECRET_KEY)

# Email Verification API
# Obtén tu API key gratuita en: https://www.abstractapi.com/api/email-verification-validation-api
# Plan gratuito: 100 verificaciones/mes
EMAIL_VERIFICATION_API_KEY = env_config('EMAIL_VERIFICATION_API_KEY', default=None)

# Email Configuration for sending emails
# Usa SendGrid si EMAIL_HOST_PASSWORD está configurado (API key presente)
# Sino, usa consola para desarrollo local
EMAIL_HOST_PASSWORD_RAW = env_config('EMAIL_HOST_PASSWORD', default='')

# Sanitizar API key: remover espacios, comillas, saltos de línea
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD_RAW.strip().strip('"').strip("'").replace('\n', '').replace('\r', '') if EMAIL_HOST_PASSWORD_RAW else ''

if EMAIL_HOST_PASSWORD:
    # SendGrid configurado - enviar emails reales
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False
    EMAIL_HOST_USER = 'apikey'
    DEFAULT_FROM_EMAIL = env_config('DEFAULT_FROM_EMAIL', default='david.ferrada@inacapmail.cl')
    
    # Debug: Log configuración y diagnóstico de API key
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"✓ SendGrid SMTP configurado")
    logger.info(f"  EMAIL_BACKEND: {EMAIL_BACKEND}")
    logger.info(f"  EMAIL_HOST: {EMAIL_HOST}:{EMAIL_PORT}")
    logger.info(f"  EMAIL_HOST_USER: {EMAIL_HOST_USER}")
    logger.info(f"  DEFAULT_FROM_EMAIL: {DEFAULT_FROM_EMAIL}")
    
    # Diagnóstico de API key (sin revelar valor completo)
    api_key_start = EMAIL_HOST_PASSWORD[:10] if len(EMAIL_HOST_PASSWORD) >= 10 else EMAIL_HOST_PASSWORD
    api_key_length = len(EMAIL_HOST_PASSWORD)
    logger.info(f"  API Key length: {api_key_length} chars")
    logger.info(f"  API Key starts with: {api_key_start}...")
    
    # Validar formato de API key de SendGrid
    if not EMAIL_HOST_PASSWORD.startswith('SG.'):
        logger.error(f"  ❌ ERROR: SendGrid API key debe empezar con 'SG.' pero empieza con '{api_key_start}'")
        logger.error(f"  ❌ Esto causará fallo en autenticación SMTP")
    else:
        logger.info(f"  ✓ API Key format looks valid (starts with 'SG.')")
else:
    # Modo desarrollo - emails en consola
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'david.ferrada@inacapmail.cl'
    
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("⚠ EMAIL_HOST_PASSWORD no configurado - usando console backend")
EMAIL_TIMEOUT = env_config('EMAIL_TIMEOUT', default=30, cast=int)
# SSL certificate verification (disable only in development if needed)
EMAIL_SSL_CERTFILE = env_config('EMAIL_SSL_CERTFILE', default=None)
EMAIL_SSL_KEYFILE = env_config('EMAIL_SSL_KEYFILE', default=None)

# Site Configuration
SITE_DOMAIN = env_config('SITE_DOMAIN', default='localhost:8000')
SITE_URL = env_config('SITE_URL', default='http://localhost:8000')


# Internationalization
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Suprimir warnings de datetimes naive en datos legacy
# Los datos antiguos pueden tener fechas sin timezone, pero no afecta la funcionalidad
import warnings
warnings.filterwarnings(
    'ignore',
    message='.*received a naive datetime.*',
    category=RuntimeWarning,
    module='django.db.models.fields'
)

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = PROJECT_ROOT / 'staticfiles'
STATICFILES_DIRS = [PROJECT_ROOT / 'frontend' / 'static']

# WhiteNoise configuration for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = PROJECT_ROOT / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# REST Framework
from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Para compatibilidad con vistas normales
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# DRF Spectacular (API Documentation)
SPECTACULAR_SETTINGS = {
    'TITLE': 'RifaTrust API',
    'DESCRIPTION': 'API REST completa para el sistema de gestión de rifas RifaTrust',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True
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
]

# Stripe Payment Settings
STRIPE_PUBLIC_KEY = env_config('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = env_config('STRIPE_SECRET_KEY', default='')

# Security Settings
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # 24 horas
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# Security Settings (Production)
if not DEBUG:
    # SECURE_SSL_REDIRECT = True  # TEMPORALMENTE DESHABILITADO PARA PRUEBAS HTTP
    SESSION_COOKIE_SECURE = False  # TEMPORALMENTE DESHABILITADO
    CSRF_COOKIE_SECURE = False  # TEMPORALMENTE DESHABILITADO
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    # SECURE_HSTS_SECONDS = 31536000  # TEMPORALMENTE DESHABILITADO
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True

# Logging Configuration - Secure error handling
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': PROJECT_ROOT / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': PROJECT_ROOT / 'logs' / 'security.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'axes': {
            'handlers': ['console', 'security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    }
}

# ============================================================================
# DJANGO-AXES: PROTECCIÓN CONTRA FUERZA BRUTA
# ============================================================================

# Backend de autenticación con Axes
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # Axes debe ir primero
    'django.contrib.auth.backends.ModelBackend',  # Backend por defecto de Django
]

# Configuración de Axes
AXES_FAILURE_LIMIT = 5  # Número de intentos fallidos antes de bloquear
AXES_COOLOFF_TIME = 1  # Horas de bloqueo (1 hora)
AXES_RESET_ON_SUCCESS = True  # Resetear intentos fallidos al login exitoso
AXES_LOCKOUT_TEMPLATE = None  # Usar mensaje de error estándar
AXES_ENABLE_ADMIN = True  # Habilitar panel de admin para Axes

# Opciones de logging
AXES_VERBOSE = True  # Logs detallados

# Usar base de datos para almacenar intentos (más seguro que cache)
AXES_HANDLER = 'axes.handlers.database.AxesDatabaseHandler'

# Lockout por IP o usuario (nueva sintaxis sin deprecation)
AXES_LOCKOUT_PARAMETERS = [
    'ip_address',  # Bloquear por IP
    'username',    # Y también por nombre de usuario
]

# Solo monitorear intentos fallidos en estas URLs
AXES_ONLY_ALLOW_FAILURES_FROM_SPECIFIC_PATH = False

# IP privadas también pueden ser bloqueadas (útil en redes internas)
AXES_NEVER_LOCKOUT_WHITELIST = False
AXES_NEVER_LOCKOUT_GET = True  # No bloquear peticiones GET

# Usar IP real del cliente (importante con proxies/load balancers)
AXES_IPWARE_PROXY_COUNT = 1  # Número de proxies entre cliente y servidor
AXES_IPWARE_META_PRECEDENCE_ORDER = [
    'HTTP_X_FORWARDED_FOR',  # Azure/nginx
    'X_FORWARDED_FOR',
    'HTTP_CLIENT_IP',
    'HTTP_X_REAL_IP',
    'HTTP_X_FORWARDED',
    'HTTP_X_CLUSTER_CLIENT_IP',
    'HTTP_FORWARDED_FOR',
    'HTTP_FORWARDED',
    'REMOTE_ADDR',
]
