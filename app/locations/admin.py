from django.contrib import admin

from locations.models import Address, City, ZipCode

models = [ZipCode, Address, City]
for item in models:
    admin.site.register(item)
