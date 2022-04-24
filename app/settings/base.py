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

DOMAIN = "www.washmix.com"
ALLOWED_HOSTS = ["*"]

SECRET_KEY = env.str("SECRET_KEY")

INSTALLED_APPS = [
    # `branding` app extends `base_site.html` from `django-jet` to
    # inject React root and should be at higher place than `django-jet`
    "branding",
    # `django-jet` has custom admin theme and should
    # be at higher place than django.contrib.admin
    "jet",
    # here we have a custom AdminSite with extra routes
    "branding.apps.BrandingConfig",
    # django
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party
    "debug_toolbar",
    "rest_framework",
    "djoser",
    "social_django",
    "swap_user",
    "swap_user.to_named_email",
    "drf_yasg",
    "djangoql",
    "django_filters",
    # local
    "orders",
    "users",
    "billing",
    "locations",
    "notifications",
    "deliveries",
    "subscriptions",
    "archived",
    # inside core app we are unregistering some models
    # it should be lower that branding apps to be last application and apply
    # last changes for admin
    "core",
]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env.str("DB_NAME", "wm_local"),
        "USER": env.str("DB_USER", "wm_user"),
        "PASSWORD": env.str("DB_PASSWORD", "wm_pass"),
        "HOST": env.str("DB_HOST", "localhost"),
        "PORT": env.str("DB_PORT", "5432"),
        "CONN_MAX_AGE": 10,
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


LANGUAGE_CODE = "en-AU"
TIME_ZONE = "America/Los_Angeles"
USE_I18N = True
USE_L10N = False
USE_TZ = True


# first element of list controls appearance in `django-jet` admin of date field
# via jet.templatetags.jet_get_date_format
DATE_INPUT_FORMATS = [
    "%m/%d/%Y",  # '10/25/2006'
    "%m/%d/%y",  # '10/25/06'
    "%Y-%m-%d",  # '2006-10-25'
    "%b %d %Y",  # 'Oct 25 2006'
    "%b %d, %Y",  # 'Oct 25, 2006'
    "%d %b %Y",  # '25 Oct 2006'
    "%d %b, %Y",  # '25 Oct, 2006'
    "%B %d %Y",  # 'October 25 2006'
    "%B %d, %Y",  # 'October 25, 2006'
    "%d %B %Y",  # '25 October 2006'
    "%d %B, %Y",  # '25 October, 2006'
]


# first element of list controls appearance in `django-jet` admin of datetime field
# via jet.templatetags.jet_get_datetime_format
DATETIME_INPUT_FORMATS = [
    "%m/%d/%Y %H:%M:%S",  # '10/25/2006 14:30:59'
    "%m/%d/%Y %H:%M:%S.%f",  # '10/25/2006 14:30:59.000200'
    "%m/%d/%Y %H:%M",  # '10/25/2006 14:30'
    "%m/%d/%Y",  # '10/25/2006'
    "%m/%d/%y %H:%M:%S",  # '10/25/06 14:30:59'
    "%m/%d/%y %H:%M:%S.%f",  # '10/25/06 14:30:59.000200'
    "%m/%d/%y %H:%M",  # '10/25/06 14:30'
    "%m/%d/%y",  # '10/25/06'
    "%Y-%m-%d %H:%M:%S",  # '2006-10-25 14:30:59'
    "%Y-%m-%d %H:%M:%S.%f",  # '2006-10-25 14:30:59.000200'
    "%Y-%m-%d %H:%M",  # '2006-10-25 14:30'
    "%Y-%m-%d",  # '2006-10-25'
]


STATIC_URL = "/assets/"
STATIC_ROOT = BASE_DIR / "assets"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

PDF_REPORTS_ROOT = MEDIA_ROOT / "reports"

WSGI_APPLICATION = "settings.wsgi.application"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
        "stdout": {
            "class": "logging.StreamHandler",
        },
    },
    # disable drf_yasg warning stuff
    "loggers": {
        "drf_yasg": {"handlers": ["null"]},
        "inspectors": {"handlers": ["null"]},
        "billing": {"handlers": ["stdout"]},
    },
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
    # Case-insensitive email for `rest-framework-simplejwt`
    "core.backends.CaseInsensitiveModelBackend",
]


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "api_evrone"
EMAIL_HOST_PASSWORD = env.str("SENDGRID_API_KEY", "")
EMAIL_PORT = 587


AUTH_USER_MODEL = "to_named_email.NamedEmailUser"

SHOW_OPENAPI_SCHEMA = True

SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = SECONDS_IN_MINUTE * 60

SESSION_COOKIE_AGE = SECONDS_IN_HOUR * 2


###########
# SIGNALS #
###########

UPDATE_FIELDS_FOR_PHONE = {"number"}
UPDATE_FIELDS_FOR_ADDRESS = {"address_line_1", "address_line_2", "zip_code"}
UPDATE_FIELDS_FOR_USER = {"first_name", "last_name", "billing_address"}


###############
# SOME PRICES #
###############

FREE_DELIVERY_PRICE = 0
PAYC_FREE_DELIVERY_FROM = 6900
GOLD_PLATINUM_FREE_DELIVERY_FROM = 5900
CREDIT_BACK_PERCENTAGE = 5
# 20$ total for rush delivery - i.e.
# - dropoff 10$ (1000)
# - pickup 10$ (1000)
RUSH_DELIVERY_PRICE = 1000


#################
# WORKING HOURS #
#################

TODAY_DELIVERY_CUT_OFF_TIME = time(hour=8)
DELIVERY_START_WORKING = time(hour=13)
DELIVERY_END_WORKING = time(hour=19)

PICKUP_SAME_DAY_START_TIMEDELTA = timedelta(hours=4)
PICKUP_SAME_DAY_END_TIMEDELTA = timedelta(hours=2)


############
# DELIVERY #
############

# 2 business days order handling + 1 day for delivery (delivery on the next day after handling)
USUAL_PROCESSING_BUSINESS_DAYS = 3
USUAL_PROCESSING_TIMEDELTA = timedelta(days=USUAL_PROCESSING_BUSINESS_DAYS)

# 1 business day order handling + 1 day for delivery (delivery on the next day after handling)
RUSH_PROCESSING_BUSINESS_DAYS = 2
RUSH_PROCESSING_TIMEDELTA = timedelta(days=RUSH_PROCESSING_BUSINESS_DAYS)

ALLOW_DELIVERY_CANCELLATION_HOURS = 3
ALLOW_DELIVERY_CANCELLATION_TIMEDELTA = timedelta(hours=ALLOW_DELIVERY_CANCELLATION_HOURS)

ALLOW_DELIVERY_RESHEDULE_HOURS = 3
ALLOW_DELIVERY_RESHEDULE_TIMEDELTA = timedelta(hours=ALLOW_DELIVERY_RESHEDULE_HOURS)

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
}
DELIVERY_DAY_CHOICES = list(DELIVERY_DAYS_MAP.items())

WORKING_DAYS = set(DELIVERY_DAYS_MAP.keys())
FULL_WEEK_DAYS = set([MON, TUE, WED, THU, FRI, SAT, SUN])
NON_WORKING_DAYS = list(FULL_WEEK_DAYS - WORKING_DAYS)

WEEKENDS_DURATION_DAYS = len(NON_WORKING_DAYS)
WEEKENDS_DURATION_TIMEDELTA = timedelta(days=WEEKENDS_DURATION_DAYS)

FULL_WEEK_DURATION_DAYS = len(FULL_WEEK_DAYS)
FULL_WEEK_DURATION_TIMEDELTA = timedelta(days=FULL_WEEK_DURATION_DAYS)

ACTIVE = "active"
PAUSED = "paused"
DELIVERY_STATUS_MAP = {
    ACTIVE: "Active recurring delivery",
    PAUSED: "Paused recurring delivery",
}
DELIVERY_STATUS_CHOICES = list(DELIVERY_STATUS_MAP.items())

#########
# USERS #
#########
DELETE_USER_AFTER_NON_SIGNUP_HOURS = 3
DELETE_USER_AFTER_TIMEDELTA = timedelta(hours=DELETE_USER_AFTER_NON_SIGNUP_HOURS)


#####################################
# APPLICATION_DATA (BUSINESS RULES) #
#####################################

DEFAULT_COUNTRY = "US"
DEFAULT_PHONE_REGION = "US"
DEFAULT_PHONE_FORMAT = PhoneNumberFormat.E164
RUSSIA_COUNTRY_CODE = 1
USA_COUNTRY_CODE = 7
ALLOWED_COUNTRY_CODES = [RUSSIA_COUNTRY_CODE, USA_COUNTRY_CODE]

CENTS_IN_DOLLAR = 100
PERCENTAGE = 100
# refill package starting from 20$
AUTO_BILLING_LIMIT = 2000

DEFAULT_ZERO_DISCOUNT = 0
DEFAULT_ZERO_AMOUNT = 0

PAYC = "payc"
GOLD = "gold"
PLATINUM = "platinum"
PACKAGE_NAME_MAP = {
    PAYC: "Pay As You Clean",
    GOLD: "Gold Tier",
    PLATINUM: "Platinum Tier",
}
PACKAGE_NAME_CHOICES = list(PACKAGE_NAME_MAP.items())
PACKAGE_NAME_ORDERING = list(PACKAGE_NAME_MAP.keys())

BASKET_ADD = "add"
BASKET_REMOVE = "remove"
BASKET_ACTION_MAP = {
    BASKET_ADD: "Add item",
    BASKET_REMOVE: "Remove",
}
BASKET_ACTION_CHOICES = list(BASKET_ACTION_MAP.items())

MAIN_TITLE = "Main"

SUBSCRIPTION_UPGRADE = "upgrade"
SUBSCRIPTION_DOWNGRADE = "downgrade"
SUBSCRIPTION_REPLENISHED = "replenished"


################################
# APPLICATION GLOBAL VARIABLES #
################################

NEXT_DAY = 1
DAYS_IN_YEAR = 365
CREDIT_BACK_PERIOD = 90

TWITTER_URL = "https://twitter.com/mix_wash/"
INSTAGRAM_URL = "https://www.instagram.com/washmix/"
FACEBOOK_URL = "https://www.facebook.com/WASHMIXOriginal/"
PHONE_NUMBER = "4​15-993-WASH [9274]"
LAUNDRY_ADDRESS = "650 Castro St, #185, Mountain View"


#########################
# DJANGO REST FRAMEWORK #
#########################

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        "api.permissions.IsClient",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
}

####################################
# DJANGO REST FRAMEWORK SIMPLE JWT #
####################################

SIMPLE_JWT = {
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=30),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(minutes=30),
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
    "EMAIL": {
        "password_reset": "notifications.emails.PasswordResetEmail",
    },
}


####################################
# TEMPLATED EMAIL (USED BY DJOSER) #
####################################

PROTOCOL = "https"
SITE_NAME = "WashMix"


#################################
# SOCIAL AUTH (LEGACY NOT USED) #
#################################

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

REDIS_DEFAULT_EXPIRATION_TIME = 60 * 60 * 23

REDIS_HOST = env.str("REDIS_HOST", "localhost")
REDIS_PORT = env.str("REDIS_PORT", "6379")
REDIS_PASSWORD = env.str("REDIS_PASSWORD", None)
REDIS_DB = 0

REDIS_SSL = env.bool("REDIS_SSL", False)
REDIS_SSL_CERT_REQS = None
REDIS_URL = env.str("REDIS_URL", None)

if not REDIS_URL:
    REDIS_CLIENT = StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        ssl=REDIS_SSL,
        ssl_cert_reqs=REDIS_SSL_CERT_REQS,
    )
else:
    REDIS_CLIENT = StrictRedis.from_url(
        url=REDIS_URL,
        db=REDIS_DB,
        ssl_cert_reqs=REDIS_SSL_CERT_REQS,
    )


############
# DRAMATIQ #
############

# 1 s - 1000 ms
MS_IN_ONE_SECOND = 1000

DRAMATIQ_DB = 1
DRAMATIQ_MAX_RETRIES = 3
DRAMATIQ_MAX_AGE = SECONDS_IN_HOUR * MS_IN_ONE_SECOND

if not REDIS_URL:
    DRAMATIQ_REDIS_CLIENT = StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=DRAMATIQ_DB,
        password=REDIS_PASSWORD,
        ssl_cert_reqs=REDIS_SSL_CERT_REQS,
    )
else:
    DRAMATIQ_REDIS_CLIENT = StrictRedis.from_url(
        url=REDIS_URL,
        db=DRAMATIQ_DB,
        ssl_cert_reqs=REDIS_SSL_CERT_REQS,
    )

DRAMATIQ_BROKER = RedisBroker(client=DRAMATIQ_REDIS_CLIENT)

# set delay for 10 s
DELIVERY_DELAY_SECONDS = 10
DRAMATIQ_DELAY_FOR_DELIVERY = DELIVERY_DELAY_SECONDS * MS_IN_ONE_SECOND

# define list of modules with tasks
DRAMATIQ_IMPORT_MODULES = [
    "billing.tasks",
    "core.tasks",
    "deliveries.tasks",
    "notifications.tasks",
]
DRAMATIQ_BROKER.add_middleware(PeriodiqMiddleware(skip_delay=30))
dramatiq.set_broker(DRAMATIQ_BROKER)


###########################
# SMS NOTIFICATION EVENTS #
###########################
USER_SIGNUP = "user_signup"
NEW_DELIVERY = "new_delivery"
DELIVERY_DROPOFF_COMPLETE = "delivery_dropoff_complete"
PICKUP_REQUEST_CANCELED = "pickup_request_canceled"
UNABLE_TO_CREATE_MULTIPLE_REQUEST = "unable_to_create_multiple_request"
PICKUP_DUE_TOMORROW = "pickup_due_tomorrow"

#############################
# TWILIO WITH SMS TEMPLATES #
#############################

TWILIO_WORKSPACE_SID = "WSf4478ac8ee039cb8fbcd416ecd762a9f"
TWILIO_NUMBER = env.str("TWILIO_NUMBER", "")
TWILIO_ACCOUNT_SID = env.str("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = env.str("TWILIO_AUTH_TOKEN", "")
TWILIO_SUCCESS = "success"
TWILIO_FAIL = "fail"
TWILIO_PICKUP_CODE = "pickup_scheduled"

SMS_EVENT_INFO = {
    USER_SIGNUP: {
        "template_name": "sms/user_signup.html",
    },
    NEW_DELIVERY: {
        "template_name": "sms/new_delivery.html",
    },
    DELIVERY_DROPOFF_COMPLETE: {
        "template_name": "sms/dropoff_complete.html",
    },
    PICKUP_REQUEST_CANCELED: {
        "template_name": "sms/pickup_request_canceled.html",
    },
    UNABLE_TO_CREATE_MULTIPLE_REQUEST: {
        "template_name": "sms/unable_to_create_multiple_request.html",
    },
    PICKUP_DUE_TOMORROW: {
        "template_name": "sms/pickup_due_tomorrow.html",
    },
}


#############################
# EMAIL NOTIFICATION EVENTS #
#############################

SIGNUP = "signup"
FORGOT_PASSWORD = "forgot_password"
PURCHASE_SUBSCRIPTION = "purchase_subscription"
NEW_REQUEST = "new_request"
NEW_ORDER = "new_order"
ACCOUNT_REMOVED = "account_removed"
PAYMENT_FAIL_CLIENT = "payment_fail_client"
PAYMENT_FAIL_ADMIN = "payment_fail_admin"
CARD_CHANGES = "card_changes"
ACCRUE_CREDIT_BACK = "accrue_credit_back"
SEND_ADMIN_CLIENT_INFORMATION = "send_admin_client_information"
SEND_ADMIN_PCUSTOMER_INFORMATION = "send_admin_pcustomer_information"
SEND_ADMIN_STORE_CREDIT = "send_email_store_credit"

#################################
# SENDGRID WITH EMAIL TEMPLATES #
#################################

SENDGRID_NO_REPLY = "no-reply@washmix.com"
SENDGRID_FROM_EMAIL = Email("info@washmix.com")
SENDGRID_API_KEY = env.str("SENDGRID_API_KEY", "")
ADMIN_EMAIL_LIST = env.list("ADMIN_EMAIL_LIST", ["michael@washmix.com"])

EMAIL_EVENT_INFO = {
    SIGNUP: {
        "template_name": "email/signup.html",
        "subject": "Welcome to Washmix!",
        "from_email": "hello@washmix.com",
    },
    FORGOT_PASSWORD: {
        "subject": "Password Reset",
        "from_email": "security@washmix.com",
    },
    PURCHASE_SUBSCRIPTION: {
        "template_name": "email/purchase_subscription.html",
        "subject": "Welcome to WashMix Advantage Program",
        "from_email": "cs@washmix.com",
    },
    NEW_ORDER: {
        "template_name": "email/new_order.html",
        "subject": "WashMix New Order",
        "from_email": "cs@washmix.com",
        "reply_to": "orders@washmix.com",
    },
    PAYMENT_FAIL_CLIENT: {
        "template_name": "email/payment_fail_client.html",
        "subject": "WashMix Payment Failed",
        "from_email": "billing@washmix.com",
        "reply_to": "billing@washmix.com",
    },
    PAYMENT_FAIL_ADMIN: {
        "template_name": "email/payment_fail_admin.html",
        "subject": "WashMix Payment Failed",
        "from_email": "info@washmix.com",
        "reply_to": "info@washmix.com",
    },
    ACCOUNT_REMOVED: {
        "template_name": "email/account_removed.html",
        "subject": "WashMix Account Removed",
        "from_email": "info@washmix.com",
        "reply_to": "info@washmix.com",
    },
    CARD_CHANGES: {
        "template_name": "email/card_changes.html",
        "subject": "Card Update",
        "from_email": "info@washmix.com",
        "reply_to": "info@washmix.com",
    },
    ACCRUE_CREDIT_BACK: {
        "template_name": "email/accrue_credit_back.html",
        "subject": "Credit Back",
        "from_email": "info@washmix.com",
        "reply_to": "info@washmix.com",
    },
    SEND_ADMIN_CLIENT_INFORMATION: {
        "template_name": "email/send_admin_client_information.html",
        "subject": "New User Activity",
        "from_email": "info@washmix.com",
        "reply_to": "info@washmix.com",
    },
    SEND_ADMIN_PCUSTOMER_INFORMATION: {
        "template_name": "email/send_admin_pcustomer_information.html",
        "subject": "New Potential Customer Activity",
        "from_email": "info@washmix.com",
        "reply_to": "info@washmix.com",
    },
    SEND_ADMIN_STORE_CREDIT: {
        "template_name": "email/send_admin_store_credit.html",
        "subject": "Store Credit Update",
        "from_email": "info@washmix.com",
        "reply_to": "info@washmix.com",
    },
}


##############
# DJANGO-JET #
##############

JET_SIDE_MENU_COMPACT = True
JET_DEFAULT_THEME = "washmix"
