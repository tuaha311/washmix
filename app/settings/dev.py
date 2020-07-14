import datetime
import os

from settings.base import *

DEBUG = True


INSTALLED_APPS += [
    "debug_toolbar",
]


TEMPLATES[0]["OPTIONS"]["debug"] = True

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
