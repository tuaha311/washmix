from django.contrib import admin

from orders.models import Item, Order, Request, Service, Price

models = [Order, Item, Request, Service, Price]
for item in models:
    admin.site.register(item)
