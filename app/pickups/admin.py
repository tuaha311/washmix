from django.contrib import admin

from pickups.models import Delivery

models = [Delivery]
for item in models:
    admin.site.register(item)
