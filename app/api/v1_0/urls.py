from django.urls import include, path

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainSlidingView,
    TokenRefreshSlidingView,
    TokenVerifyView,
)

from api.v1_0.views import auth, health, services, trigger
from billing.views import cards, checkout, choose, coupons, packages, payments
from core import views as core_views
from locations.views import addresses, locations, zip_codes
from orders import views as order_views
from pickups.views import deliveries
from users.views import customers, profile

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

subscription_urls = (
    [
        # packages and subscription payment views:
        # 1. please, choose a subscription - we will return Invoice.id and attach subscription to Invoice,
        # also, we store this data between screens.
        path("choose/", choose.ChooseView.as_view(), name="choose"),
        # 2. please, if you have a coupon - apply it to the Invoice.id
        path("apply_coupon/", coupons.ApplyCouponView.as_view(), name="apply-coupon"),
        # 3. submit all your personal and address data
        path("checkout/", checkout.CheckoutView.as_view(), name="checkout"),
    ],
    "subscription",
)

billing_urls = (
    [
        # billing via Stripe related methods:
        # 1. we are creating CreateIntentView object to link Card.id with Client.id for later processing
        path("create_intent/", payments.CreateIntentView.as_view(), name="setup-intent"),
        # 2. we receive success webhook from Stripe and create an Transaction
        path("stripe_webhook/", payments.StripeWebhookView.as_view(), name="stripe-webhook"),
    ],
    "billing",
)

router = SimpleRouter(trailing_slash=True)
router.register("addresses", addresses.AddressViewSet, basename="addresses")
router.register("phones", core_views.PhoneViewSet, basename="phones")
router.register("orders", order_views.OrderViewSet, basename="orders")
router.register("cards", cards.CardViewSet, basename="cards")
router.register("deliveries", deliveries.DeliveryViewSet, basename="deliveries")

urlpatterns = [
    # closed methods that require authorization
    *router.urls,
    path("profile/", profile.ProfileView.as_view(), name="profile"),
    path("zip_codes/", zip_codes.ZipCodeListView.as_view(), name="zip-code-list"),
    path("billing/", include(billing_urls)),
    path("subscription/", include(subscription_urls)),
    path("trigger/", trigger.TriggerView.as_view(), name="trigger"),
    # open methods without authorization (landing page, authorization, health check)
    path("jwt/", include(token_urls)),
    path("auth/", include(auth_urls)),
    path("packages/", packages.PackageListView.as_view(), name="package-list"),
    path("locations/", locations.LocationListView.as_view(), name="location-list"),
    path("services/", services.ServiceListView.as_view(), name="service-list"),
    path("customers/", customers.CustomerCreateView.as_view(), name="customer-create"),
    path("health/", health.HealthView.as_view(), name="ping"),
]
