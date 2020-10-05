from django.urls import include, path

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshSlidingView, TokenVerifyView

from api.v1_0.views import auth, services, trigger, twilio
from billing.views import cards, packages
from core import views as core_views
from locations.views import addresses, locations, zip_codes
from orders.views import basket, orders
from pickups.views import deliveries, schedules
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


basket_urls = (
    [
        # 1. you can view items in basket
        path("", basket.BasketView.as_view(), name="basket"),
        # 2. add or remove items from basket
        path("change_item/", basket.ChangeItemView.as_view(), name="change-item"),
        # 3. you can clear whole basket
        path("clear/", basket.ClearView.as_view(), name="clear"),
        # 4. checkout
        path("checkout/", basket.CheckoutView.as_view(), name="checkout"),
    ],
    "basket",
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
    *router.urls,
    path("profile/", profile.ProfileView.as_view(), name="profile"),
    path("zip_codes/", zip_codes.ZipCodeListView.as_view(), name="zip-code-list"),
    path("billing/", include("billing.urls.billing")),
    path("subscription/", include("billing.urls.subscription")),
    path("invoices/", include("billing.urls.invoices")),
    path("basket/", include(basket_urls)),
    path("sms/", include(sms_urls)),
    path("trigger/", trigger.TriggerView.as_view(), name="trigger"),
    # open methods without authorization (landing page, authorization, health check)
    path("jwt/", include(token_urls)),
    path("auth/", include(auth_urls)),
    path("packages/", packages.PackageListView.as_view(), name="package-list"),
    path("locations/", locations.LocationListView.as_view(), name="location-list"),
    path("services/", services.ServiceListView.as_view(), name="service-list"),
    path("customers/", customers.CustomerCreateView.as_view(), name="customer-create"),
]
