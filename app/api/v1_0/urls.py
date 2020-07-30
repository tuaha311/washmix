from django.urls import include, path

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainSlidingView,
    TokenRefreshSlidingView,
    TokenVerifyView,
)

from api.v1_0.views import addresses, auth, orders, packages, zip_codes

router = SimpleRouter(trailing_slash=True)
router.register("addresses", addresses.AddressViewSet, basename="address")
router.register("orders", orders.OrderViewSet, basename="order")
router.register("zip_codes", zip_codes.ZipCodeViewSet, basename="zip-codes")

app_name = "v1_0"
token_urls = (
    [
        path("refresh/", TokenRefreshSlidingView.as_view(), name="refresh"),
        path("verify/", TokenVerifyView.as_view(), name="verify"),
    ],
    "jwt",
)

auth_urls = (
    [
        path("login/", TokenObtainSlidingView.as_view(), name="obtain"),
        path("signup/", auth.SignupView.as_view({"post": "create"}), name="signup"),
        path(
            "forgot_password/",
            auth.ForgotPasswordView.as_view({"post": "reset_password"}),
            name="forgot-password",
        ),
        path(
            "reset_new_password/",
            auth.SetNewPasswordView.as_view({"post": "reset_password_confirm"}),
            name="set-new-password",
        ),
    ],
    "auth",
)


urlpatterns = [
    *router.urls,
    path("jwt/", include(token_urls)),
    path("auth/", include(auth_urls)),
    path("packages/", packages.PackageListView.as_view(), name="package-list"),
]
