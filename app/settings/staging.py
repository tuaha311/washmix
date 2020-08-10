import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from settings.base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]


sentry_sdk.init(
    dsn="https://cf2158b8940747c78607487f5a2ef3ca@o430742.ingest.sentry.io/5379821",
    integrations=[DjangoIntegration()],
    send_default_pii=True,
)
