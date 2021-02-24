import datetime
import os

from settings.base import *

DEBUG = True

DEV_ONLY_APPS = []
INSTALLED_APPS += DEV_ONLY_APPS


MIDDLEWARE = [
    "core.middleware.logging_middleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


INTERNAL_IPS = [
    "127.0.0.1",
]

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
