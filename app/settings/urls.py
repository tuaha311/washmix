from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path, re_path

from api.views import auth, coupons, login, oauth, orders, products, refresh_token, stripe, users
from core.admin import admin_site

urlpatterns = []


if settings.DEBUG:
    urlpatterns += [
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
    ]


users_patterns = [
    re_path(r"^(?P<id>\d+)?/?(?P<app_users>[A-Z_]+)?/?$", users.Users.as_view()),
]

auth_patterns = [
    re_path(r"^login/$", login.LoginUser.as_view()),
    re_path(r"^logout/$", refresh_token.logout_user),
    re_path(r"^refresh-token/$", refresh_token.RefreshTokenView.as_view()),
    re_path(r"^social-login/$", oauth.OAuth.as_view()),
    re_path(r"^activate/$", users.UserActivationView.as_view()),
]


urlpatterns += [
    #
    # Include block
    #
    path("auth/", include(auth_patterns)),
    path("users/", include(users_patterns)),
    # path("users/", include("djoser.urls")),
    re_path(r"^admin/", admin_site.urls),
    re_path(r"^auth/", include("rest_framework_social_oauth2.urls")),
    re_path(r"^o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
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
