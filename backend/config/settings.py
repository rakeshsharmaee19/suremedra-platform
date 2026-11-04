"""
Django settings for the Suremedra platform.

All environment-specific values come from environment variables (or a .env.example file
next to manage.py). See .env.example for the full list.
"""
import sys
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env.example")

# ---------------------------------------------------------------- core ------
DEBUG = env.bool("DJANGO_DEBUG", default=False)
TESTING = sys.argv[1:2] == ["test"]
SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-dev-key-change-me" if (DEBUG or TESTING) else "")
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY is not set. Copy .env.example to .env.example (development) or set it in .env.example.prod (production)."
    )
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"] if DEBUG else [])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

SITE_URL = env("SITE_URL", default="http://localhost:3000")  # public website
ADMIN_URL = env("ADMIN_URL", default="http://localhost:8000")  # where /admin/ lives (used in emails)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "simple_history",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    # project apps
    "core",
    "catalog",
    "enquiries",
    "billing",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "core.middleware.RequestLoggingMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ------------------------------------------------------------ database ------
# Default is SQLite so the project runs with zero setup. Use PostgreSQL in
# staging/production:  DATABASE_URL=postgres://user:pass@host:5432/dbname
DATABASES = {"default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------ static files and media ----
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="ap-south-1")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}
if AWS_STORAGE_BUCKET_NAME:
    # Private bucket. Credentials come from the EC2 instance role (no keys in .env.example).
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME,
            "location": "media",
            "default_acl": None,
            "querystring_auth": True,
            "querystring_expire": 600,
            "file_overwrite": False,
        },
    }

# -------------------------------------------------------- reverse proxy -----
# Caddy terminates HTTPS and forwards X-Forwarded-Proto / X-Forwarded-For.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
NUM_PROXIES = env.int("NUM_PROXIES", default=0)  # set to 1 behind Caddy

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=3600)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    X_FRAME_OPTIONS = "DENY"

# -------------------------------------------------------- DRF and CORS -----
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": env("THROTTLE_ANON", default="120/min"),
        "enquiry": env("THROTTLE_ENQUIRY", default="5/hour"),
    },
    "NUM_PROXIES": NUM_PROXIES or None,
    "EXCEPTION_HANDLER": "core.api.exception_handler",
}
SPECTACULAR_SETTINGS = {
    "TITLE": "Suremedra Platform API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# ------------------------------------------------------------- celery -------
REDIS_URL = env("REDIS_URL", default="")
CELERY_BROKER_URL = REDIS_URL or "memory://"
# Without Redis (local dev / tests) tasks simply run inline.
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=not REDIS_URL)
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_TASK_TIME_LIMIT = 120
CELERY_TASK_ACKS_LATE = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TIMEZONE = TIME_ZONE

# -------------------------------------------------------------- email -------
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend" if DEBUG else "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_TIMEOUT = 20
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="Suremedra <notifications@localhost>")
# Extra addresses that receive new-enquiry alerts (in addition to Admin/SuperAdmin users).
ADMIN_NOTIFICATION_EMAILS = env.list("ADMIN_NOTIFICATION_EMAILS", default=[])

# ------------------------------------------------------ business config ----
TURNSTILE_SECRET_KEY = env("TURNSTILE_SECRET_KEY", default="")  # empty = CAPTCHA check disabled

COMPANY = {
    "name": env("COMPANY_NAME", default="Suremedra Enterprises Private Limited"),
    "address": env("COMPANY_ADDRESS", default="Plot 14, Sector 6, Industrial Area, Gurugram, Haryana 122001, India"),
    "gstin": env("COMPANY_GSTIN", default=""),
    "email": env("COMPANY_EMAIL", default="enquiries@suremedra.com"),
    "phone": env("COMPANY_PHONE", default=""),
    "bank_details": env("COMPANY_BANK_DETAILS", default=""),
    "invoice_terms": env(
        "INVOICE_TERMS",
        default="This is a proforma invoice and does not constitute a tax invoice. "
        "Prices and availability are valid for 7 days from the date of issue.",
    ),
}

# ------------------------------------------------------------ admin 2FA -----
ADMIN_2FA = env.bool("ADMIN_2FA", default=False)

# ------------------------------------------------------------- logging ------
LOG_LEVEL = env("LOG_LEVEL", default="INFO")
LOG_FORMAT = env("LOG_FORMAT", default="text")  # "text" or "json"
LOG_TO_FILE = env.bool("LOG_TO_FILE", default=False)
LOG_DIR = Path(env("LOG_DIR", default=str(BASE_DIR / "logs")))

_handlers = ["console"]
_handler_defs = {
    "console": {
        "class": "logging.StreamHandler",
        "formatter": "json" if LOG_FORMAT == "json" else "text",
        "filters": ["request_id"],
    }
}
if LOG_TO_FILE:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    _handler_defs["file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": str(LOG_DIR / "app.log"),
        "maxBytes": 10 * 1024 * 1024,
        "backupCount": 5,
        "encoding": "utf-8",
        "formatter": "json" if LOG_FORMAT == "json" else "text",
        "filters": ["request_id"],
    }
    _handlers.append("file")

if TESTING:
    import logging as _logging

    _logging.disable(_logging.INFO)  # keep test output readable; warnings and errors still show

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"request_id": {"()": "core.logging.RequestIDFilter"}},
    "formatters": {
        "text": {"format": "%(asctime)s %(levelname)-7s [%(request_id)s] %(name)s: %(message)s"},
        "json": {"()": "core.logging.JsonFormatter"},
    },
    "handlers": _handler_defs,
    "root": {"handlers": _handlers, "level": LOG_LEVEL},
    "loggers": {
        "django": {"handlers": _handlers, "level": "INFO", "propagate": False},
        "django.request": {"handlers": _handlers, "level": "WARNING", "propagate": False},
        "django.security": {"handlers": _handlers, "level": "WARNING", "propagate": False},
        "celery": {"handlers": _handlers, "level": LOG_LEVEL, "propagate": False},
        # Our own code: use logging.getLogger(__name__) and it lands here.
        "core": {"handlers": _handlers, "level": LOG_LEVEL, "propagate": False},
        "catalog": {"handlers": _handlers, "level": LOG_LEVEL, "propagate": False},
        "enquiries": {"handlers": _handlers, "level": LOG_LEVEL, "propagate": False},
        "billing": {"handlers": _handlers, "level": LOG_LEVEL, "propagate": False},
    },
}
