from rest_framework.routers import SimpleRouter

from api.v1_0.views import addresses, orders

router = SimpleRouter(trailing_slash=False)
router.register("addresses", addresses.AddressViewSet.as_view())
router.register("orders", orders.OrderViewSet.as_view())


urlpatterns = [*router.urls]
