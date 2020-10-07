from django.urls import include, path

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshSlidingView, TokenVerifyView

from api.v1_0.views import auth, services, trigger, twilio
from billing.views import cards
from core import views as core_views
from deliveries.views import deliveries, schedules
from locations.views import addresses, locations, zip_codes
from orders.views import orders
from subscriptions.views import packages
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
        path("login/", auth.LoginView.as_view(), name="obtain"),
        path("signup/", auth.SignupView.as_view(), name="signup"),
        path("forgot_password/", auth.ForgotPasswordView.as_view(), name="forgot-password",),
        path("reset_new_password/", auth.SetNewPasswordView.as_view(), name="reset-new-password",),
    ],
    "auth",
)


sms_urls = (
    [path("twilio_webhook/", twilio.TwilioFlexWebhookView.as_view(), name="flex-webhook"),],
    "sms",
)


router = SimpleRouter(trailing_slash=True)
router.register("addresses", addresses.AddressViewSet, basename="addresses")
router.register("phones", core_views.PhoneViewSet, basename="phones")
router.register("orders", orders.OrderViewSet, basename="orders")
router.register("cards", cards.CardViewSet, basename="cards")
router.register("deliveries", deliveries.DeliveryViewSet, basename="deliveries")
router.register("schedules", schedules.ScheduleViewSet, basename="schedules")

urlpatterns = [
    # closed methods that require authorization
    path("profile/", profile.ProfileView.as_view(), name="profile"),
    path("zip_codes/", zip_codes.ZipCodeListView.as_view(), name="zip-code-list"),
    path("sms/", include(sms_urls)),
    path("trigger/", trigger.TriggerView.as_view(), name="trigger"),
    path("billing/", include("billing.urls.billing")),
    path("subscription/", include("billing.urls.subscription")),
    path("invoices/", include("billing.urls.invoices")),
    path("basket/", include("orders.urls.baskets")),
    path("orders/", include("orders.urls.orders")),
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
