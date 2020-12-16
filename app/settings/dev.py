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

ALLOWED_COUNTRY_CODES = [1, 7]
