from django.contrib import admin

from subscriptions.models import Package

models = [Package]
for item in models:
    admin.site.register(item)
