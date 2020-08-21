from django.urls import include, path

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainSlidingView,
    TokenRefreshSlidingView,
    TokenVerifyView,
)

from api.v1_0.views import (
    addresses,
    auth,
    coupons,
    customers,
    health,
    locations,
    orders,
    packages,
    payments,
    phones,
    profile,
    services,
    zip_codes,
)

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
        path("signup/", auth.SignupView.as_view(), name="signup"),
        path("forgot_password/", auth.ForgotPasswordView.as_view(), name="forgot-password",),
        path("reset_new_password/", auth.SetNewPasswordView.as_view(), name="reset-new-password",),
    ],
    "auth",
)

billing_urls = (
    [
        path("create_payment/", payments.CreatePaymentsView.as_view(), name="create-payments"),
        path("stripe_webhook/", payments.StripeWebhookView.as_view(), name="stripe-webhook"),
        path("apply_coupon/", coupons.ApplyCouponView.as_view(), name="apply-coupon"),
    ],
    "billing",
)

router = SimpleRouter(trailing_slash=True)
router.register("addresses", addresses.AddressViewSet, basename="address")
router.register("phones", phones.PhoneViewSet, basename="phones")
router.register("orders", orders.OrderViewSet, basename="order")

urlpatterns = [
    # closed methods that require authorization
    *router.urls,
    path("profile/", profile.ProfileView.as_view(), name="profile"),
    path("zip_codes/", zip_codes.ZipCodeListView.as_view(), name="zip-code-list"),
    path("set_package/", packages.SetPackageView.as_view(), name="set-package"),
    path("billing/", include(billing_urls)),
    # open methods without authorization (landing page, authorization, health check)
    path("jwt/", include(token_urls)),
    path("auth/", include(auth_urls)),
    path("packages/", packages.PackageListView.as_view(), name="package-list"),
    path("locations/", locations.LocationListView.as_view(), name="location-list"),
    path("services/", services.ServiceListView.as_view(), name="service-list"),
    path("customers/", customers.CustomerCreateView.as_view(), name="customer-create"),
    path("health/", health.HealthView.as_view(), name="ping"),
]
