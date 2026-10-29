
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega as variáveis do arquivo .env localizado na raiz do projeto.
# Variáveis já definidas no ambiente têm prioridade.
load_dotenv(BASE_DIR / ".env")

# Configurações principais
SECRET_KEY = os.environ.get(
    "NEXO_SECRET_KEY",
    "dev-only-change-before-production-nexo-studio",
)

DEBUG = os.environ.get(
    "NEXO_DEBUG", "1"
).lower() in ("1", "true", "yes")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "NEXO_ALLOWED_HOSTS", "*" if DEBUG else ""
    ).split(",")
    if host.strip()
]

# Origens confiáveis para envio de formulários via HTTPS.
# Configure os domínios no .env, separados por vírgula.
CSRF_TRUSTED_ORIGINS = [
    'https://*.github.dev',
    'https://*.app.github.dev',
    'http://localhost:8000',
    'https://localhost:8000',
]

# Aplicações
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "studio",
    "security.apps.SecurityConfig",
]

# Middlewares
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "security.middleware.SecurityHeadersMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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
                "studio.context_processors.business_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Banco de dados SQLite
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Autenticação
AUTH_PASSWORD_VALIDATORS = []

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "landing"

# Localização
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Arquivos estáticos e enviados
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Cache local para demonstração em um único processo.
# Em produção, utilizar cache compartilhado, como Redis.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "nexo-studio-security",
    }
}

# Proteções de cookies
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# Proteções adicionais fora do modo de desenvolvimento
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_SSL_REDIRECT = (
        os.environ.get("NEXO_SECURE_SSL_REDIRECT", "1").lower()
        not in ("0", "false", "no")
    )

    SECURE_HSTS_SECONDS = int(
        os.environ.get("NEXO_HSTS_SECONDS", "0")
    )
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
