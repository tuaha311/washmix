import datetime
import os

from settings.base import *

DEBUG = True


INSTALLED_APPS += [
    "debug_toolbar",
]


MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
