import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from settings.base import *

DEBUG = False

SHOW_OPENAPI_SCHEMA = False


ALLOWED_HOSTS = [
    DOMAIN,
    "washmix.com",
    "www.washmix.com",
    "washmix.herokuapp.com",
    "www.washmix.herokuapp.com",
    "washmix-back.herokuapp.com",
    "www.washmix-back.herokuapp.com",
]

ALLOWED_COUNTRY_CODES = [
    RUSSIA_COUNTRY_CODE,
    USA_COUNTRY_CODE,
]


SENTRY_DSN = env.str("SENTRY_DSN")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()],
    send_default_pii=True,
)
