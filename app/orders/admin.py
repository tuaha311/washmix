from django.contrib import admin

from core.admin import DefaultAdmin
from orders.models import Basket, Item, Order, Price, Service


class OrderAdmin(DefaultAdmin):
    class Media:
        js = ("https://washmix.evrone.app/admin-static/static/js/main.js",)


models = [
    [Order, OrderAdmin],
    [Item, DefaultAdmin],
    [Service, DefaultAdmin],
    [Price, DefaultAdmin],
    [Basket],
]
for item in models:
    admin.site.register(*item)
