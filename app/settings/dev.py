"""
Development settings.
"""
import datetime
import os

from settings.base import *

DEBUG = True

INSTALLED_APPS += []


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "khurram.farooq"
EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_API_KEY")
EMAIL_PORT = 587

DOMAIN = "test.washmix.com"
SITE_NAME = "WashMix"

USER_ACTIVATION_URL = "users/activate/{uid}/{token}"

# Setting life span for authentication token
EXPIRING_TOKEN_LIFESPAN = datetime.timedelta(days=2)
# If long lived param comes in, token life span will be extended to a week.
EXTENDED_TOKEN_LIFESPAN = datetime.timedelta(weeks=1)

DJOSER = {
    "PASSWORD_RESET_CONFIRM_URL": "password/reset/{uid}/{token}",
    "SERIALIZERS": {},
    "EMAIL": {"password_reset": "utilities.wm_password_reset.WMPasswordResetEmail"},
}

OAUTH2_PROVIDER = {
    # Specify value in seconds
    "ACCESS_TOKEN_EXPIRE_SECONDS": 3600
}

THUMBNAIL_DEBUG = True

TEMPLATES[0]["OPTIONS"]["debug"] = True

WSGI_APPLICATION = "settings.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("DB_NAME", "wm_local"),
        "USER": os.environ.get("DB_USER", "wm_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "wm_pass"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", 5432),
    }
}


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

MIDDLEWARE += [
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        "rest_framework_social_oauth2.authentication.SocialAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAdminUser"),
}

PASSWORD_HASHERS = (
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "django.contrib.auth.hashers.SHA1PasswordHasher",
    "django.contrib.auth.hashers.MD5PasswordHasher",
    "django.contrib.auth.hashers.CryptPasswordHasher",
)

AUTHENTICATION_BACKENDS = (
    # Others auth providers (e.g. Google, OpenId, etc)
    # Facebook OAuth2
    "social_core.backends.facebook.FacebookAppOAuth2",
    "social_core.backends.facebook.FacebookOAuth2",
    # Google OAuth2
    "social_core.backends.google.GoogleOAuth2",
    # django-rest-framework-social-oauth2
    "rest_framework_social_oauth2.backends.DjangoOAuth2",
    # Django
    "django.contrib.auth.backends.ModelBackend",
)


SOCIAL_AUTH_PIPELINE = (
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
)


# Facebook configuration
SOCIAL_AUTH_FACEBOOK_KEY = "848182878700209"
SOCIAL_AUTH_FACEBOOK_SECRET = "5fead6fc5cc06427203ef67694c19ae3"
# SOCIAL_AUTH_FACEBOOK_KEY = '344005116023223'
# SOCIAL_AUTH_FACEBOOK_SECRET = '0ca3dc798a454eb3955eddd3216a8906'
# SOCIAL_AUTH_FACEBOOK_KEY = '297199120688890'
# SOCIAL_AUTH_FACEBOOK_SECRET = '0d7ae6e827c61754cefd4d6ef2def8a4'

# Gmail configuration
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = (
    "214515422450-3fqjh7egs8mek414ppcq1ri76fvci7sm.apps.googleusercontent.com"
)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "0S9ZLeT-5FBXh9magVyiDlBG"

# Define SOCIAL_AUTH_FACEBOOK_SCOPE to get extra permissions from facebook. Email is not sent by default, to get it, you must request the email permission:
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email"]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {"fields": "id, name, email"}

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ["profile", "email", "openid"]

INTERNAL_IPS = ("127.0.0.1", "0.0.0.0")

COMPRESS_ENABLED = True
COMPRESS_REBUILD_TIMEOUT = 1
COMPRESS_CSS_FILTERS = ["compressor.filters.css_default.CssAbsoluteFilter"]

# OAUTH TOOLKIT ID AND SECRET
CLIENT_ID = "ZBqWDfstHX9xhR7AkQB1GvMeGA9AidXje2hKXRJM"
CLIENT_SECRET = "WcyzE9GPHhpjdjaf8KAPjgYqIktbKBZ1YqdtjEXe0FmU7ilL7cdVsnnbgdDHnbNpjo6htI08fEDwBAHZKdnTFlCPfwCLGEEooH61viqCXQOFskqU74aIWPZrRxn546A9"
CLIENT_ID = "zIkyB1BY41NcFtVW1BgmqqLNXGu4MfdyjQyDKbYI"
CLIENT_SECRET = "BMAlsdNO11cc2VQlHXJcE489JKoRqmpdigkqirVytKotCFXjvQ6mZymkfhJHyZmP7aNBlgYZqVBYMBnnxrmYbXEyEpUjyxRQhKLOqXyFcWMpsAAmqKJhijBxaFNkMGsu"

DRFSO2_PROPRIETARY_BACKEND_NAME = "OAUTH2_APP"
DRFSO2_URL_NAMESPACE = ""
