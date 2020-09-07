from django.contrib import admin

from pickups.models import Delivery, Interval

models = [Interval, Delivery]
for item in models:
    admin.site.register(item)
