from django.contrib import admin

from subscriptions.models import Package, Subscription

models = [Subscription, Package]
for item in models:
    admin.site.register(item)
