from django.contrib import admin

from core.admin import DefaultAdmin
from deliveries.models import Delivery, Request


class RequestAdmin(DefaultAdmin):
    list_display = [
        "__str__",
        "client",
        "address",
        "comment",
        "is_rush",
        "pickup_date",
        "dropoff_date",
    ]


class DeliveryAdmin(DefaultAdmin):
    list_display = [
        "__str__",
        "date",
        "priority",
        "employee",
        "kind",
        "status",
        "address",
        "is_rush",
        "note",
        "comment",
    ]
    list_editable = [
        "date",
        "employee",
        "status",
        "priority",
    ]
    list_filter = [
        "status",
        "kind",
    ]


models = [[Delivery, DeliveryAdmin], [Request, RequestAdmin]]
for item in models:
    admin.site.register(*item)
