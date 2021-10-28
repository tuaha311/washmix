from django.contrib import admin

from archived.models import ArchivedDelivery, ArchivedRequest
from deliveries.admin import DeliveryAdmin, RequestAdmin
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.models import Delivery, Request


class ArchivedDeliveriesAdmin(DeliveryAdmin):
    def get_queryset(self, request):
        return Delivery.objects.filter(
            status__in=[DeliveryStatus.COMPLETED, DeliveryStatus.CANCELLED]
        )


class ArchivedRequestsAdmin(RequestAdmin):
    def get_queryset(self, request):
        return Request.objects.filter(
            delivery_list__kind=DeliveryKind.DROPOFF,
            delivery_list__status__in=[DeliveryStatus.COMPLETED, DeliveryStatus.CANCELLED],
        )


models = [[ArchivedDelivery, ArchivedDeliveriesAdmin], [ArchivedRequest, ArchivedRequestsAdmin]]

for item in models:
    admin.site.register(*item)
