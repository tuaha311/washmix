from django.contrib import admin

from core.admin import DefaultAdmin
from locations.models import City, ZipCode

models = [[ZipCode, DefaultAdmin], [City, DefaultAdmin]]
for item in models:
    admin.site.register(*item)
