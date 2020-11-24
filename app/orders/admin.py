from django.contrib import admin

from core.admin import DefaultAdmin
from orders.models import Item, Order, Price, Service
from other.media import Media


class OrderAdmin(DefaultAdmin):
    Media = Media


models = [
    [Order, OrderAdmin],
    [Item, DefaultAdmin],
    [Service, DefaultAdmin],
    [Price, DefaultAdmin],
]
for item in models:
    admin.site.register(*item)
