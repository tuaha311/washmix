from django.contrib import admin

from orders.models import Item, Order, Price, Request, Service

models = [Order, Item, Request, Service, Price]
for item in models:
    admin.site.register(item)
