import datetime
import os

from settings.base import *

DEBUG = True


INSTALLED_APPS += [
    "debug_toolbar",
]


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

THUMBNAIL_DEBUG = True

TEMPLATES[0]["OPTIONS"]["debug"] = True

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
