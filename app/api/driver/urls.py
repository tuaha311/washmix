from rest_framework.routers import SimpleRouter

from deliveries.api.driver.views import DeliveryViewSet

router = SimpleRouter(trailing_slash=True)
router.register("deliveries", DeliveryViewSet, basename="deliveries")

app_name = "driver"


urlpatterns = [*router.urls]
