from django.contrib import admin

from orders.models import Item, Order, Request, Service

models = [Order, Item, Request, Service]
for item in models:
    admin.site.register(item)
