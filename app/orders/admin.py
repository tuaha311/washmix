from django.contrib import admin

from orders.models import Item, Order, Price, Service

models = [Order, Item, Service, Price]
for item in models:
    admin.site.register(item)
