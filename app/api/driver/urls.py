from django.urls import include, path

from rest_framework.routers import SimpleRouter

from api.client.views.auth import LoginView
from deliveries.api.driver.views import DeliveryViewSet

router = SimpleRouter(trailing_slash=True)
router.register("deliveries", DeliveryViewSet, basename="deliveries")

app_name = "driver"


auth_urls = (
    [
        path("login/", LoginView.as_view(), name="obtain"),
    ],
    "auth",
)


urlpatterns = [
    *router.urls,
    path("auth/", include(auth_urls)),
]
