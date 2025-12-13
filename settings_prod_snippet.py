import os
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

# Set DEBUG from environment variable. Default to False for production.
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# This snippet should be integrated into your core/settings.py file.
# Place the following code block within your main settings file,
# ideally after basic settings and inside an `if not DEBUG:` condition.

if not DEBUG:
    # Production settings

    # SECURITY WARNING: Keep the production secret key secret!
    # Render will inject a generated SECRET_KEY into the environment.
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ImproperlyConfigured("SECRET_KEY environment variable not set.")

    # Allowed hosts for production. Render provides the external hostname.
    RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if not RENDER_EXTERNAL_HOSTNAME:
        # This should always be set by Render in production environments.
        # If it's not, it's a critical configuration error.
        raise ImproperlyConfigured("RENDER_EXTERNAL_HOSTNAME environment variable not set in production.")
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME]
    # CSRF_TRUSTED_ORIGINS should include your Render domain for security.
    CSRF_TRUSTED_ORIGINS = [f"https://{RENDER_EXTERNAL_HOSTNAME}"]

    # Database configuration using dj_database_url to parse the DATABASE_URL.
    # Render automatically provides DATABASE_URL from the linked PostgreSQL service.
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }

    # Static files configuration for Whitenoise.
    # Ensure 'whitenoise.middleware.WhiteNoiseMiddleware' is added to your MIDDLEWARE list,
    # preferably right after 'django.middleware.security.SecurityMiddleware'.
    # Also, ensure 'whitenoise' is in your requirements.txt.
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'staticfiles')

    # Whitenoise storage backend for compressed and cached static files.
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

    # Security settings for production environment.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True # Redirect HTTP to HTTPS
    SESSION_COOKIE_SECURE = True # Transmit cookies only over HTTPS
    CSRF_COOKIE_SECURE = True # Transmit CSRF cookie only over HTTPS
    SECURE_HSTS_SECONDS = 31536000 # HSTS for 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True # Enable XSS protection
    X_FRAME_OPTIONS = 'DENY' # Prevent clickjacking

    # Production logging configuration.
    # Logs to console (stdout/stderr) are captured by Render.
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
            'gunicorn.error': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
            'gunicorn.access': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
            '': { # Root logger
                'handlers': ['console'],
                'level': 'INFO',
            }
        },
    }
