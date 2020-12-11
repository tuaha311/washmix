from django.contrib import admin

from core.admin import DefaultAdmin
from deliveries.models import Delivery, Request


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
        "comment",
    ]
    list_editable = [
        "employee",
        "status",
        "priority",
    ]
    list_filter = [
        "status",
        "kind",
    ]


models = [[Delivery, DeliveryAdmin], [Request, DefaultAdmin]]
for item in models:
    admin.site.register(*item)
