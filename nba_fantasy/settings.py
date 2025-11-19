import os
from pathlib import Path

# -------------------------
# BASE DIR
# -------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------
# SECURITY
# -------------------------
SECRET_KEY = "django-insecure-CHANGE_THIS_KEY"  # troque por uma chave segura
DEBUG = True
ALLOWED_HOSTS = []

# -------------------------
# APPS INSTALLED
# -------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Apps do projeto
    "core",

    # Terceiros
    "rest_framework",
]

# -------------------------
# MIDDLEWARE
# -------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -------------------------
# ROOT URLS
# -------------------------
ROOT_URLCONF = "nba_fantasy.urls"

# -------------------------
# TEMPLATES (padrão Django)
# -------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # caso queira templates
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# -------------------------
# WSGI / ASGI
# -------------------------
WSGI_APPLICATION = "nba_fantasy.wsgi.application"
ASGI_APPLICATION = "nba_fantasy.asgi.application"

# -------------------------
# DATABASE (SQLite para dev)
# -------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# -------------------------
# PASSWORD VALIDATION
# -------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# -------------------------
# LANGUAGE & TIMEZONE
# -------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------
# STATIC FILES
# -------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

# -------------------------
# DEFAULT AUTO FIELD
# -------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------
# CUSTOM USER MODEL
# -------------------------
AUTH_USER_MODEL = "core.User"  # se você usar User customizado

# -------------------------
# DJANGO REST FRAMEWORK
# -------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        # "rest_framework_simplejwt.authentication.JWTAuthentication",  # se quiser JWT
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
}
