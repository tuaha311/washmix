from django.contrib import admin

from core.admin import DefaultAdmin
from locations.models import Address, City, ZipCode

models = [[ZipCode, DefaultAdmin], [Address, DefaultAdmin], [City, DefaultAdmin]]
for item in models:
    admin.site.register(*item)
