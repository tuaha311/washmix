from django.contrib import admin

from core.admin import DefaultAdmin
from deliveries.models import Delivery, Request


class DeliveryInlineAdmin(admin.TabularInline):
    model = Delivery
    extra = 1


class RequestAdmin(DefaultAdmin):
    inlines = [DeliveryInlineAdmin]
    list_display = [
        "__str__",
        "client",
        "address",
        "comment",
        "is_rush",
        "pickup_date",
        "pickup_status",
        "dropoff_date",
        "dropoff_status",
    ]


class DeliveryAdmin(DefaultAdmin):
    list_display = [
        "__str__",
        "date",
        "sorting",
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
        "sorting",
    ]
    list_filter = [
        "status",
        "kind",
    ]


models = [[Delivery, DeliveryAdmin], [Request, RequestAdmin]]
for item in models:
    admin.site.register(*item)
