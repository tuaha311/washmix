from datetime import time, timedelta
from pathlib import Path

import dramatiq
import stripe
from dramatiq.brokers.redis import RedisBroker
from environs import Env
from periodiq import PeriodiqMiddleware
from phonenumbers import PhoneNumberFormat
from redis import StrictRedis
from sendgrid.helpers.mail import Email

env = Env()

env.read_env()

BASE_DIR = Path(__file__).parents[1]


##########
# DJANGO #
##########

DOMAIN = "washmix.evrone.app"
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
    "djoser",
    "social_django",
    "swap_user",
    "swap_user.named_email",
    "drf_yasg",
]

LOCAL_APPS = [
    "core",
    "orders",
    "users",
    "billing",
    "locations",
    "notifications",
    "deliveries",
    "subscriptions",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env.str("DB_NAME", "wm_local"),
        "USER": env.str("DB_USER", "wm_user"),
        "PASSWORD": env.str("DB_PASSWORD", "wm_pass"),
        "HOST": env.str("DB_HOST", "localhost"),
        "PORT": env.str("DB_PORT", "5432"),
    }
}


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

ROOT_URLCONF = "settings.urls"

REMINDER_TIME = 15


LANGUAGE_CODE = "en-AU"
TIME_ZONE = "America/Los_Angeles"
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = "/assets/"
STATIC_ROOT = BASE_DIR / "assets"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

WSGI_APPLICATION = "settings.wsgi.application"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"null": {"class": "logging.NullHandler",},},
    # disable drf_yasg warning stuff
    "loggers": {"drf_yasg": {"handlers": ["null"]}, "inspectors": {"handlers": ["null"]},},
}


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [],
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
EMAIL_HOST_USER = "api_evrone"
EMAIL_HOST_PASSWORD = env.str("SENDGRID_API_KEY", "")
EMAIL_PORT = 587


AUTH_USER_MODEL = "swap_user_named_email.NamedEmailUser"


#####################################
# APPLICATION_DATA (BUSINESS RULES) #
#####################################

DEFAULT_PHONE_REGION = "US"
DEFAULT_PHONE_FORMAT = PhoneNumberFormat.E164
ALLOWED_COUNTRY_CODES = [1, 7]

CENTS_IN_DOLLAR = 100
PERCENTAGE = 100

DEFAULT_ZERO_DISCOUNT = 0

PAYC = "payc"
GOLD = "gold"
PLATINUM = "platinum"
PACKAGE_NAME_MAP = {
    PAYC: "PAYC",
    GOLD: "GOLD",
    PLATINUM: "PLATINUM",
}
PACKAGE_NAME_CHOICES = list(PACKAGE_NAME_MAP.items())

BASKET_ADD = "add"
BASKET_REMOVE = "remove"
BASKET_ACTION_MAP = {
    BASKET_ADD: "Add item",
    BASKET_REMOVE: "Remove",
}
BASKET_ACTION_CHOICES = list(BASKET_ACTION_MAP.items())

MAIN_TITLE = "Main"


##########################
# DELIVERY HANDLING INFO #
##########################

ORDER_PROCESSING_BUSINESS_DAYS = 3
ORDER_PROCESSING_TIMEDELTA = timedelta(days=ORDER_PROCESSING_BUSINESS_DAYS)
WEEKENDS_DURATION_DAYS = 2
WEEKENDS_DURATION_TIMEDELTA = timedelta(days=WEEKENDS_DURATION_DAYS)
NON_WORKING_ISO_WEEKENDS = [6, 7]


###############
# SOME PRICES #
###############

FREE_DELIVERY_PRICE = 0
PAYC_FREE_DELIVERY_THRESHOLD = 4900
GOLD_PLATINUM_FREE_DELIVERY_THRESHOLD = 3900


#################
# WORKING HOURS #
#################

TODAY_DELIVERY_CUT_OFF_TIME = time(hour=9)
DELIVERY_START_WORKING = time(hour=9)
DELIVERY_END_WORKING = time(hour=18)


############
# DELIVERY #
############

MON = 1
TUE = 2
WED = 3
THU = 4
FRI = 5
SAT = 6
SUN = 7
DELIVERY_DAYS_MAP = {
    MON: "Monday",
    TUE: "Tuesday",
    WED: "Wednesday",
    THU: "Thursday",
    FRI: "Friday",
    SAT: "Saturday",
    SUN: "Sunday",
}
DELIVERY_DAY_CHOICES = list(DELIVERY_DAYS_MAP.items())

ACTIVE = "active"
PAUSED = "paused"
DELIVERY_STATUS_MAP = {
    ACTIVE: "Active recurring delivery",
    PAUSED: "Paused recurring delivery",
}
DELIVERY_STATUS_CHOICES = list(DELIVERY_STATUS_MAP.items())


################
# PICKUPS INFO #
################

PICKUP_SAME_DAY_START_TIMEDELTA = timedelta(hours=4)
PICKUP_SAME_DAY_END_TIMEDELTA = timedelta(hours=2)


################################
# APPLICATION GLOBAL VARIABLES #
################################

BUSINESS_DAYS = 5
FULL_WEEK_LENGTH = 7
NEXT_DAY = 1
DAYS_IN_YEAR = 365
CREDIT_BACK_PERIOD = 90

TWITTER_URL = "https://twitter.com/mix_wash/"
INSTAGRAM_URL = "https://www.instagram.com/washmix/"
FACEBOOK_URL = "https://www.facebook.com/WASHMIXOriginal/"


#########################
# DJANGO REST FRAMEWORK #
#########################

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer",],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser",],
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


############
# DRF-YASG #
############

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {"Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}},
    "DEFAULT_AUTO_SCHEMA_CLASS": "api.inspectors.WashMixAutoSchema",
}


##########
# STRIPE #
##########

STRIPE_PUBLIC_KEY = env.str("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = env.str("STRIPE_SECRET_KEY", "")
stripe.api_key = STRIPE_SECRET_KEY

STRIPE_WEBHOOK_IP_WHITELIST = [
    "3.18.12.63",
    "3.130.192.231",
    "13.235.14.237",
    "13.235.122.149",
    "35.154.171.200",
    "52.15.183.38",
    "54.187.174.169",
    "54.187.205.235",
    "54.187.216.72",
    "54.241.31.99",
    "54.241.31.102",
    "54.241.34.107",
]


##########
# DJOSER #
##########

DJOSER = {
    "PASSWORD_RESET_CONFIRM_URL": "password/reset/confirm/{uid}/{token}",
    "USERNAME_RESET_CONFIRM_URL": "username/reset/confirm/{uid}/{token}",
    "ACTIVATION_URL": "activate/{uid}/{token}",
    "SEND_ACTIVATION_EMAIL": True,
    "SEND_CONFIRMATION_EMAIL": True,
    "USER_CREATE_PASSWORD_RETYPE": False,
    "PASSWORD_RESET_CONFIRM_RETYPE": False,
    "TOKEN_MODEL": None,
    "EMAIL": {"password_reset": "core.emails.PasswordResetEmail",},
}


####################################
# TEMPLATED EMAIL (USED BY DJOSER) #
####################################

PROTOCOL = "https"
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


#########
# REDIS #
#########

REDIS_HOST = env.str("REDIS_HOST", "localhost")
REDIS_PORT = env.str("REDIS_PORT", "6379")
REDIS_DB = 0
REDIS_URL = f"{REDIS_HOST}:{REDIS_PORT}"
REDIS_CLIENT = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,)
REDIS_DEFAULT_EXPIRATION_TIME = 60 * 60 * 23


############
# DRAMATIQ #
############

DRAMATIQ_DB = 1
DRAMATIQ_REDIS_URL = f"redis://{REDIS_URL}/{DRAMATIQ_DB}"
DRAMATIQ_BROKER = RedisBroker(url=DRAMATIQ_REDIS_URL)

# define list of modules with tasks
DRAMATIQ_IMPORT_MODULES = [
    "core.tasks",
    "billing.tasks",
    "deliveries.tasks",
]
DRAMATIQ_BROKER.add_middleware(PeriodiqMiddleware(skip_delay=30))
dramatiq.set_broker(DRAMATIQ_BROKER)


##########
# TWILIO #
##########

TWILIO_NUMBER = env.str("TWILIO_NUMBER", "")
TWILIO_ACCOUNT_SID = env.str("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = env.str("TWILIO_AUTH_TOKEN", "")
TWILIO_SUCCESS = "success"
TWILIO_FAIL = "fail"
TWILIO_PICKUP_CODE = "pickup_scheduled"


############
# SENDGRID #
############

SENDGRID_FROM_EMAIL = Email("info@washmix.com")
SENDGRID_API_KEY = env.str("SENDGRID_API_KEY", "")

SIGNUP = "signup"
FORGOT_PASSWORD = "forgot_password"
EMAIL_EVENT_INFO = {
    SIGNUP: {
        "template_name": "welcome.html",
        "subject": "Welcome to Washmix!",
        "from_email": "hello@washmix.com",
    },
    FORGOT_PASSWORD: {"subject": "Password Reset", "from_email": "security@washmix.com",},
}


####################
# DJANGO-SWAP-USER #
####################

SWAP_USER = {"EMAIL_USER_ABSTRACT_BASE_CLASS": "swap_user.models.email.AbstractNamedEmailUser"}
