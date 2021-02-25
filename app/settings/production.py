import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from settings.base import *

DEBUG = False

SECURE_SSL_REDIRECT = True

ALLOWED_HOSTS = [
    "washmix.com",
    "washmix.herokuapp.com",
    "washmix-back.herokuapp.com",
]

ALLOWED_COUNTRY_CODES = [USA_COUNTRY_CODE]


SENTRY_DSN = env.str("SENTRY_DSN")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()],
    send_default_pii=True,
)
