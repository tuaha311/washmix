from django.urls import path
from deliveries.admin import DeliveryAdmin

from deliveries.api.pos.views import POSRequestUpdateView

request_urls = (
    [
        path("update/", POSRequestUpdateView.as_view(), name="update"),
    ],
    "request",
)

urlpatterns = [
    path("update-deliveries/", DeliveryAdmin.update_deliveries, name="update-deliveries"),
]