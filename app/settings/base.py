import os

from django.conf.global_settings import STATICFILES_FINDERS

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


##########
# DJANGO #
##########

ALLOWED_HOSTS = ["*"]

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
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_expiring_authtoken",
    "rest_framework_social_oauth2",
    "django_dramatiq",
    "compressor",
    "clear_cache",
    "markdown_deux",
    "robots",
    "djoser",
    "oauth2_provider",
    "social_django",
    "django_cleanup",
]

LOCAL_APPS = [
    "core",
    "orders",
    "users",
    "billing",
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

ROOT_URLCONF = "settings.urls"

TEAM_WASHMIX = "+14159939274"

REMINDER_TIME = 15


LANGUAGE_CODE = "en-AU"
TIME_ZONE = "US/Pacific"
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "../static")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATICFILES_FINDERS += ("compressor.finders.CompressorFinder",)

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "../media")


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [os.path.join(BASE_DIR, "core/templates")],
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]


###############
# APPLICATION #
###############

API_URL = "https://api.washmix.com"

##########
# OAUTH2 #
##########

OAUTH2_PROVIDER = {
    "SCOPES": {"read": "Read scope", "write": "Write scope",},
    "CLIENT_ID_GENERATOR_CLASS": "oauth2_provider.generators.ClientIdGenerator",
    "CLIENT_SECRET_GENERATOR_CLASS": "oauth2_provider.generators.ClientSecretGenerator",
}

##############
# COMPRESSOR #
##############

COMPRESS_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)

THUMBNAIL_ALTERNATIVE_RESOLUTIONS = [1.5, 2]
THUMBNAIL_ORIENTATION = False
