from django.contrib import admin

from orders.models import Item, Order

models = [Order, Item]
for item in models:
    admin.site.register(item)
