import importlib
import os

import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.staging")

django.setup()

for item in settings.DRAMATIQ_IMPORT_MODULES:
    importlib.import_module(item)
