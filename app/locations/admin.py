from django.contrib import admin

from core.admin import AdminWithSearch
from locations.models import Address, City, ZipCode

models = [[ZipCode, AdminWithSearch], [City, AdminWithSearch], [Address, AdminWithSearch]]
for item in models:
    admin.site.register(*item)
