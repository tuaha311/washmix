from django.contrib import admin

from core.models import Address, Notification, Package, Product

models = [Package, Product, Address, Notification]
for item in models:
    admin.site.register(item)
