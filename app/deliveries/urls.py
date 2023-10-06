from django.urls import path

from deliveries.api.pos.views import POSRequestUpdateView

request_urls = (
    [
        path("update/", POSRequestUpdateView.as_view(), name="update"),
    ],
    "request",
)

urlpatterns = []