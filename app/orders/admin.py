from django.contrib import admin

from core.admin import DefaultAdmin
from orders.models import Item, Order, Price, Service


class OrderAdmin(DefaultAdmin):
    class Media:
        js = ("https://washmix.evrone.app/admin-static/static/js/main.js",)
        css = {"all": ("https://washmix.evrone.app/admin-static/static/css/main.css",)}


models = [
    [Order, OrderAdmin],
    [Item, DefaultAdmin],
    [Service, DefaultAdmin],
    [Price, DefaultAdmin],
]
for item in models:
    admin.site.register(*item)
