import datetime
import os

from settings.base import *

DEBUG = True

DEV_ONLY_APPS = ["corsheaders"]
INSTALLED_APPS += DEV_ONLY_APPS


MIDDLEWARE = [
    "core.middleware.logging_middleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "users.middlewares.superadmin_middleware.SuperAdminVerificationMiddleware",
    "users.middlewares.driver_middleware.DriverVerificationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# INTERNAL_IPS = ["127.0.0.1", "localhost"]


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "settings.dev.show_toolbar",
}

ALLOWED_COUNTRY_CODES = [RUSSIA_COUNTRY_CODE, USA_COUNTRY_CODE]


####################################
# DJANGO REST FRAMEWORK SIMPLE JWT #
####################################

SIMPLE_JWT = {
    "SLIDING_TOKEN_LIFETIME": timedelta(days=7),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=7),
    "SIGNING_KEY": env.str("SIMPLE_JWT_SIGNING_KEY"),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.SlidingToken",),
}

CORS_ALLOW_ALL_ORIGINS = True
