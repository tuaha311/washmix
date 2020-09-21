from django.contrib import admin

from orders.models import Basket, Item, Order, Price, Service

models = [Order, Item, Service, Price, Basket]
for item in models:
    admin.site.register(item)
