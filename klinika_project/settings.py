import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET KEY (must be provided via environment)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('DJANGO_SECRET_KEY must be set in environment')

# DEBUG flag from environment (defaults to False for safety)
def _env_bool(name: str, default: str = 'False') -> bool:
    return os.getenv(name, default).strip().lower() in ('1', 'true', 'yes', 'on')

DEBUG = _env_bool('DEBUG', 'False')

# Hosts from environment: comma-separated. Defaults to '*' only in DEBUG.
_hosts = os.getenv('ALLOWED_HOSTS', '')
if _hosts:
    ALLOWED_HOSTS = [h.strip() for h in _hosts.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = ['*'] if DEBUG else []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Local apps
    'accounts',
    'doctors',
    'patients',
    'appointments',
    'payments',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'klinika_project.middleware.CleanupOldAppointmentsMiddleware',
]

ROOT_URLCONF = 'klinika_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dashboard.context_processors.clinic_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'klinika_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'klinika_db',       # Bazaning nomi
        'USER': 'postgres',         # PostgreSQL foydalanuvchi nomi
        'PASSWORD': 'parol_yoz',    # Foydalanuvchi paroli
        'HOST': 'localhost',        # Agar aHost yoki tashqi serverda bo‘lsa, IP yoki domen yoziladi
        'PORT': '5432',             # Standart port
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'uz'
LANGUAGES = [
    ('uz', "O'zbekcha"),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = os.getenv('STATIC_URL', '/static/')
# Allow overriding static root via env; default to 'staticfiles'
STATIC_ROOT = Path(os.getenv('STATIC_ROOT', str(BASE_DIR / 'staticfiles')))
# Use project 'static' folder as source in development; avoid pointing to same as STATIC_ROOT
_project_static = BASE_DIR / 'static'
if _project_static.resolve() != STATIC_ROOT.resolve() and _project_static.exists():
    STATICFILES_DIRS = [_project_static]
else:
    STATICFILES_DIRS = []

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_URL = '/accounts/login/'

# (Removed email console backend used for password reset)

# Media files (user uploads)
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
MEDIA_ROOT = Path(os.getenv('MEDIA_ROOT', str(BASE_DIR / 'media')))
if ('runserver' in sys.argv or DEBUG) and not MEDIA_ROOT.exists():
    try:
        MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

# Override DB settings from environment if provided
DATABASES.setdefault('default', {})
DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
DATABASES['default']['NAME'] = os.getenv('DB_NAME', DATABASES['default'].get('NAME', 'klinika_db'))
DATABASES['default']['USER'] = os.getenv('DB_USER', DATABASES['default'].get('USER', 'postgres'))
DATABASES['default']['PASSWORD'] = os.getenv('DB_PASSWORD', DATABASES['default'].get('PASSWORD', ''))
DATABASES['default']['HOST'] = os.getenv('DB_HOST', DATABASES['default'].get('HOST', 'localhost'))
DATABASES['default']['PORT'] = os.getenv('DB_PORT', DATABASES['default'].get('PORT', '5432'))

# Security settings (sensible defaults in production, overridable via env)
SECURE_SSL_REDIRECT = _env_bool('SECURE_SSL_REDIRECT', 'False' if DEBUG else 'True')
SESSION_COOKIE_SECURE = _env_bool('SESSION_COOKIE_SECURE', 'False' if DEBUG else 'True')
CSRF_COOKIE_SECURE = _env_bool('CSRF_COOKIE_SECURE', 'False' if DEBUG else 'True')
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0' if DEBUG else '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False' if DEBUG else 'True')
SECURE_HSTS_PRELOAD = _env_bool('SECURE_HSTS_PRELOAD', 'False' if DEBUG else 'True')

# Optional: proxy SSL header for reverse proxies (e.g., Nginx)
_proxy_header = os.getenv('SECURE_PROXY_SSL_HEADER', '')
if _proxy_header:
    # Expect format like: HTTP_X_FORWARDED_PROTO,https
    parts = [p.strip() for p in _proxy_header.split(',')]
    if len(parts) == 2 and parts[0] and parts[1]:
        SECURE_PROXY_SSL_HEADER = (parts[0], parts[1])

# CSRF trusted origins (comma-separated, include scheme)
_csrf_origins = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if _csrf_origins:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split(',') if o.strip()]

# Relax security for local runserver unless explicitly disabled
if 'runserver' in sys.argv and _env_bool('ALLOW_HTTP_RUNSERVER', 'True'):
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Basic logging configuration
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': LOG_LEVEL,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
}
