import datetime
import os

from settings.base import *

DEBUG = True


INSTALLED_APPS += [
    "debug_toolbar",
]


USER_ACTIVATION_URL = "users/activate/{uid}/{token}"

DJOSER = {
    "PASSWORD_RESET_CONFIRM_URL": "password/reset/{uid}/{token}",
    "SERIALIZERS": {},
    "EMAIL": {"password_reset": "utilities.wm_password_reset.WMPasswordResetEmail"},
}

TEMPLATES[0]["OPTIONS"]["debug"] = True

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
