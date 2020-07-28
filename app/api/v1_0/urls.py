from django.urls import include, path

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenVerifyView
from rest_framework_simplejwt.views import TokenObtainSlidingView, TokenRefreshSlidingView

from api.v1_0.views import addresses, orders, packages, zip_codes

router = SimpleRouter(trailing_slash=True)
router.register("addresses", addresses.AddressViewSet, basename="address")
router.register("orders", orders.OrderViewSet, basename="order")
router.register("zip_codes", zip_codes.ZipCodeViewSet, basename="zip-codes")

app_name = "v1_0"
token_urls = (
    [
        path("obtain/", TokenObtainSlidingView.as_view(), name="obtain"),
        path("refresh/", TokenRefreshSlidingView.as_view(), name="refresh"),
        path("verify/", TokenVerifyView.as_view(), name="verify"),
    ],
    "token",
)


urlpatterns = [
    *router.urls,
    path("token/", include(token_urls)),
    path("auth/", include("djoser.urls")),
    path("packages/", packages.PackageListView.as_view(), name="package-list"),
]
