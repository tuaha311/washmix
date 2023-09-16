from django import forms
from django.contrib import admin
from users.admin import CustomAutocompleteSelect

from archived.models import ArchivedCustomer, ArchivedDelivery, ArchivedRequest
from core.admin import AdminWithSearch
from deliveries.admin import ArchivedDeliveryAdmin, RequestAdmin
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.models import Delivery, Request


class ArchivedDeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = "__all__"
        widgets = {
            "employee": CustomAutocompleteSelect(
                model._meta.get_field("employee").remote_field, "Select an Employee", admin.site
            )
        }
    
    
class ArchivedDeliveriesAdmin(ArchivedDeliveryAdmin):
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
        "phone",
        "email",
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
