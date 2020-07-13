from django.urls import include, path

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from api.v1_0.views import addresses, orders, packages

router = SimpleRouter(trailing_slash=False)
router.register("addresses", addresses.AddressViewSet, basename="address")
router.register("orders", orders.OrderViewSet, basename="order")

app_name = "v1_0"
auth_urls = (
    [
        path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
        path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
        path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    ],
    "auth",
)


urlpatterns = [
    path("auth/", include(auth_urls)),
    path("packages/", packages.ListAPIView.as_view(), name="package-list"),
] + router.urls
