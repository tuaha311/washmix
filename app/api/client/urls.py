from django.urls import include, path

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshSlidingView, TokenVerifyView

from api.client.views import auth, checkout, prepare, services, trigger, twilio
from billing.api.views import cards, invoices
from core.api import views as core_views
from deliveries.api.client.views import requests, schedules
from locations.api.views import addresses, locations, zip_codes
from subscriptions.api.views import packages
from users.api.views import customers, profile

app_name = "client"
token_urls = (
    [
        path("refresh/", TokenRefreshSlidingView.as_view(), name="refresh"),
        path("verify/", TokenVerifyView.as_view(), name="verify"),
    ],
    "jwt",
)

auth_urls = (
    [
        path("login/", auth.LoginView.as_view(), name="obtain"),
        path("signup/", auth.SignupView.as_view(), name="signup"),
        path(
            "forgot_password/",
            auth.ForgotPasswordView.as_view(),
            name="forgot-password",
        ),
        path(
            "reset_new_password/",
            auth.SetNewPasswordView.as_view(),
            name="reset-new-password",
        ),
    ],
    "auth",
)


sms_urls = (
    [
        path("delivery/", twilio.TwilioFlexDeliveryWebhookView.as_view(), name="delivery"),
        path(
            "online_workers/", twilio.TwilioFlexOnlineWorkersWebhookView.as_view(), name="workers"
        ),
    ],
    "sms",
)

welcome_urls = (
    [
        path("checkout/", checkout.WelcomeCheckoutView.as_view(), name="checkout"),
    ],
    "welcome",
)


router = SimpleRouter(trailing_slash=True)
router.register("addresses", addresses.AddressViewSet, basename="addresses")
router.register("phones", core_views.PhoneViewSet, basename="phones")
router.register("cards", cards.CardViewSet, basename="cards")
router.register("schedules", schedules.ScheduleViewSet, basename="schedules")
router.register("requests", requests.RequestViewSet, basename="requests")

urlpatterns = [
    # closed methods that require authorization
    path("profile/", profile.ProfileView.as_view(), name="profile"),
    path("zip_codes/", zip_codes.ZipCodeListView.as_view(), name="zip-code-list"),
    path("sms/", include(sms_urls)),
    path("welcome/", include(welcome_urls)),
    path("trigger/", trigger.TriggerView.as_view(), name="trigger"),
    path("billing/", include("billing.urls.client")),
    path("orders/", include("orders.urls.client")),
    path("subscription/", include("subscriptions.urls.client")),
    path("invoices/", invoices.InvoiceListView.as_view(), name="invoice-list"),
    # default routes has a higher priority under router URLS
    *router.urls,
    # open methods without authorization (landing page, authorization, health check)
    path("jwt/", include(token_urls)),
    path("auth/", include(auth_urls)),
    path("packages/", packages.PackageListView.as_view(), name="package-list"),
    path("locations/", locations.LocationListView.as_view(), name="location-list"),
    path("services/", services.ServiceListView.as_view(), name="service-list"),
    path("customers/", customers.CustomerCreateView.as_view(), name="customer-create"),
]
