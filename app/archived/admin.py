from django.contrib import admin

from archived.models import ArchivedCustomer, ArchivedDelivery, ArchivedRequest
from core.admin import AdminWithSearch
from deliveries.admin import DeliveryAdmin, RequestAdmin
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.models import Delivery, Request


class ArchivedDeliveriesAdmin(DeliveryAdmin):
    def get_queryset(self, request):
        return Delivery.objects.filter(
            status__in=[DeliveryStatus.COMPLETED, DeliveryStatus.CANCELLED, DeliveryStatus.NO_SHOW]
        )


class ArchivedRequestsAdmin(RequestAdmin):
    def get_queryset(self, request):
        return Request.objects.filter(
            delivery_list__kind=DeliveryKind.DROPOFF,
            delivery_list__status__in=[
                DeliveryStatus.COMPLETED,
                DeliveryStatus.CANCELLED,
                DeliveryStatus.NO_SHOW,
            ],
        )


class ArchivedCustomerAdmin(AdminWithSearch):
    list_display = [
        "__str__",
        "full_name",
        "email",
        "phone",
        "zip_code",
        "address",
        "kind",
    ]
    list_filter = ["kind"]


models = [
    [ArchivedDelivery, ArchivedDeliveriesAdmin],
    [ArchivedRequest, ArchivedRequestsAdmin],
    [ArchivedCustomer, ArchivedCustomerAdmin],
]

for item in models:
    admin.site.register(*item)
