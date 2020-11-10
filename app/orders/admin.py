from django.contrib import admin

from core.admin import DefaultAdmin
from orders.models import Basket, Item, Order, Price, Service


class OrderAdmin(DefaultAdmin):
    class Media:
        js = (
            "https://washmix.evrone.app/admin-static/static/js/main.a621e94d.chunk.js",
            "https://washmix.evrone.app/admin-static/static/js/runtime-main.64509596.js",
        )


models = [
    [Order, OrderAdmin],
    [Item, DefaultAdmin],
    [Service, DefaultAdmin],
    [Price, DefaultAdmin],
    [Basket],
]
for item in models:
    admin.site.register(*item)
