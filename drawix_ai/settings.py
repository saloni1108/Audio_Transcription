import os
from pathlib import Path
from datetime import timedelta
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "transcribe",
    "blog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "darwix_ai.rate_limit.RateLimitMiddleware",
]

ROOT_URLCONF = "darwix_ai.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    }
]
WSGI_APPLICATION = "darwix_ai.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": urlparse(os.getenv("DATABASE_URL", "postgres://darwix:darwix@db:5432/darwix")).path.lstrip("/"),
        "USER": urlparse(os.getenv("DATABASE_URL")).username,
        "PASSWORD": urlparse(os.getenv("DATABASE_URL")).password,
        "HOST": urlparse(os.getenv("DATABASE_URL")).hostname,
        "PORT": urlparse(os.getenv("DATABASE_URL")).port,
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Darwix AI Microservice API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

from loguru import logger  # noqa

CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_TASK_ALWAYS_EAGER = False

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_TTL_MIN", "60"))),
}

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_REGION = os.getenv("S3_REGION")

RATE_LIMIT_RPM = int(os.getenv("RATE_LIMIT_RPM", "30"))
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

DIARIZATION_BACKEND = os.getenv("DIARIZATION_BACKEND", "ecapa_onnx")
SENTENCE_TRANSFORMER = os.getenv("SENTENCE_TRANSFORMER", "sentence-transformers/all-MiniLM-L6-v2")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")