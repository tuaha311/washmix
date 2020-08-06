import datetime
import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from settings.base import *

DEBUG = True


INSTALLED_APPS += []


MIDDLEWARE += []


sentry_sdk.init(
    dsn="https://cf2158b8940747c78607487f5a2ef3ca@o430742.ingest.sentry.io/5379821",
    integrations=[DjangoIntegration()],
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)
