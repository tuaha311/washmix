"""
Django settings for wm_django project.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""
import os
import sys

# from debug_toolbar.middleware import DebugToolbarMiddleware
from django.conf.global_settings import STATICFILES_FINDERS

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret away!
SECRET_KEY = "^8x5j(d(4h#+rw*g1_@ul8dk-5kdm3+dgsg2!$&k7!no2bj19v"

SITE_ID = 1

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_cleanup",
    "compressor",
    "clear_cache",
    "markdown_deux",
    "robots",
]

# Django Cleanup should be the very last app in the tuple.
LOCAL_APPS = [
    "core",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
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

ROOT_URLCONF = "urls"

TEAM_WASHMIX = "+14159939274"

REMINDER_TIME = 15

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/
LANGUAGE_CODE = "en-AU"
TIME_ZONE = "US/Pacific"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images) and Media files
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "../static")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATICFILES_FINDERS += ("compressor.finders.CompressorFinder",)
MEDIA_URL = "/m/"
MEDIA_ROOT = os.path.join(BASE_DIR, "../media_root")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.request",
                # 'django.template.context_processors.tz',
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

OAUTH2_PROVIDER = {
    "SCOPES": {"read": "Read scope", "write": "Write scope",},
    "CLIENT_ID_GENERATOR_CLASS": "oauth2_provider.generators.ClientIdGenerator",
    "CLIENT_SECRET_GENERATOR_CLASS": "oauth2_provider.generators.ClientSecretGenerator",
}

# Django compressor settings
# http://django-compressor.readthedocs.org/en/latest/settings/
COMPRESS_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)

# Sorl Thumbnail.
THUMBNAIL_ALTERNATIVE_RESOLUTIONS = [1.5, 2]
THUMBNAIL_ORIENTATION = False

# TODO: once development is complete we should remove this from base settings and secure it -Amir
ALLOWED_HOSTS = ["*"]
