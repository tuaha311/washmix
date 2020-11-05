from django.contrib import admin

from core.admin import DefaultAdmin
from orders.models import Basket, Item, Order, Price, Service

models = [
    [Order, DefaultAdmin],
    [Item, DefaultAdmin],
    [Service, DefaultAdmin],
    [Price, DefaultAdmin],
    [Basket],
]
for item in models:
    admin.site.register(*item)
