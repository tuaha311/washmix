from django.conf.urls import include
from django.contrib.auth import views as auth_views
from django.urls import path, re_path

from api.legacy.views import auth, coupons, orders, products, stripe, users
from core.admin import admin_site

app_name = "legacy"

users_patterns = (
    [re_path(r"^(?P<id>\d+)?/?(?P<app_users>[A-Z_]+)?/?$", users.Users.as_view()),],
    "users",
)


urlpatterns = [
    #
    # Include block
    #
    path("users/", include(users_patterns)),
    # path("users/", include("djoser.urls")),
    re_path(r"^admin/", admin_site.urls),
    #
    # Views block
    #
    re_path(r"^orders/(?P<id>\d+)?/?$", orders.Orders.as_view()),
    re_path(r"^purchases/(?P<type>[a-z_]+)?/?(?P<id>\d+)?/?$", stripe.Cards.as_view()),
    re_path(r"^coupons/", coupons.CouponView.as_view()),
    re_path(r"^products/(?P<id>\d+)?/?$", products.ProductView.as_view()),
    path("password_reset/", auth.PasswordResetViewCustom.as_view()),
    path(
        "admin/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "admin/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
