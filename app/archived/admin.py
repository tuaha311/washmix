# Register your models here.
from django.contrib import admin
from django.utils.timezone import localtime

from archived.models import ArchivedDelivery, ArchivedRequest
from deliveries.admin import DeliveryAdmin, RequestAdmin
from deliveries.models import Delivery, Request
from settings.base import DISPLAY_REQUEST_DELIVERIES_TIMEDELTA


class ArchivedDeliveriesAdmin(DeliveryAdmin):
    def get_queryset(self, request):
        return Delivery.objects.filter(
            created__lt=localtime() - DISPLAY_REQUEST_DELIVERIES_TIMEDELTA
        )


class ArchivedRequestsAdmin(RequestAdmin):
    def get_queryset(self, request):
        return Request.objects.filter(
            created__lt=localtime() - DISPLAY_REQUEST_DELIVERIES_TIMEDELTA
        )


models = [[ArchivedDelivery, ArchivedDeliveriesAdmin], [ArchivedRequest, ArchivedRequestsAdmin]]

for item in models:
    admin.site.register(*item)
