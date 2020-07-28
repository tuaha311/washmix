import os
from datetime import timedelta

from django.conf.global_settings import STATICFILES_FINDERS

from environs import Env

env = Env()

env.read_env()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


##########
# DJANGO #
##########

ALLOWED_HOSTS = ["*"]

SECRET_KEY = env.str("SECRET_KEY")

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_dramatiq",
    "compressor",
    "clear_cache",
    "markdown_deux",
    "djoser",
    "social_django",
    "django_cleanup",
    "swap_user",
]

LOCAL_APPS = [
    "core",
    "orders",
    "users",
    "billing",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env.str("DB_NAME", "wm_local"),
        "USER": env.str("DB_USER", "wm_user"),
        "PASSWORD": env.str("PASSWORD", "wm_pass"),
        "HOST": env.str("DB_HOST", "localhost"),
        "PORT": env.str("DB_PORT", "5432"),
    }
}


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

WSGI_APPLICATION = "settings.wsgi.application"


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
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    # Facebook OAuth2
    "social_core.backends.facebook.FacebookAppOAuth2",
    "social_core.backends.facebook.FacebookOAuth2",
    # Google OAuth2
    "social_core.backends.google.GoogleOAuth2",
    # Django
    "django.contrib.auth.backends.ModelBackend",
]


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "khurram.farooq"
EMAIL_HOST_PASSWORD = env.str("SENDGRID_API_KEY")
EMAIL_PORT = 587


AUTH_USER_MODEL = "swap_user.EmailUser"


#########################
# DJANGO REST FRAMEWORK #
#########################

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

####################################
# DJANGO REST FRAMEWORK SIMPLE JWT #
####################################

SIMPLE_JWT = {
    "SLIDING_TOKEN_LIFETIME": timedelta(days=1),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=7),
    "SIGNING_KEY": env.str("SIMPLE_JWT_SIGNING_KEY"),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.SlidingToken",),
}


##########
# DJOSER #
##########

DJOSER = {
    "PASSWORD_RESET_CONFIRM_URL": "#/password/reset/confirm/{uid}/{token}",
    "USERNAME_RESET_CONFIRM_URL": "#/username/reset/confirm/{uid}/{token}",
    "ACTIVATION_URL": "#/activate/{uid}/{token}",
    "SEND_ACTIVATION_EMAIL": True,
    "SEND_CONFIRMATION_EMAIL": True,
    "USER_CREATE_PASSWORD_RETYPE": True,
    "TOKEN_MODEL": None,
}


####################################
# TEMPLATED EMAIL (USED BY DJOSER) #
####################################

DOMAIN = "washmix.com"
SITE_NAME = "WashMix"


###############
# SOCIAL AUTH #
###############

SOCIAL_AUTH_POSTGRES_JSONFIELD = True

SOCIAL_AUTH_PIPELINE = [
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.social_auth.social_user",
    "social.pipeline.check_email_exists",
    "social_core.pipeline.user.create_user",
    "social.pipeline.add_additional_social_userinfo",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "social_core.pipeline.social_auth.associate_by_email",
]


SOCIAL_AUTH_FACEBOOK_KEY = "848182878700209"
SOCIAL_AUTH_FACEBOOK_SECRET = "5fead6fc5cc06427203ef67694c19ae3"
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email"]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {"fields": "id, name, email"}

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = (
    "214515422450-3fqjh7egs8mek414ppcq1ri76fvci7sm.apps.googleusercontent.com"
)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "0S9ZLeT-5FBXh9magVyiDlBG"
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ["profile", "email", "openid"]


############
# DRAMATIQ #
############

DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {"url": "redis://localhost:6379/0"},
    "MIDDLEWARE": [
        "dramatiq.middleware.Prometheus",
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Callbacks",
        "dramatiq.middleware.Retries",
        "django_dramatiq.middleware.AdminMiddleware",
        "django_dramatiq.middleware.DbConnectionsMiddleware",
    ],
}


##########
# TWILIO #
##########

TWILIO_NUMBER = env.str("TWILIO_NUMBER")
TWILIO_ACCOUNT_SID = env.str("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = env.str("TWILIO_AUTH_TOKEN")
