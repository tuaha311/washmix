import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from settings.base import *

DEBUG = True

ALLOWED_HOSTS = [
    DOMAIN,
    "localhost",
    "washmix.herokuapp.com",
    "washmix-back.herokuapp.com",
]

ALLOWED_COUNTRY_CODES = [1, 7]


SENTRY_DSN = env.str("SENTRY_DSN")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()],
    send_default_pii=True,
)
