from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from rest_framework import routers

from modules.helpers import admin_site
from api.views import coupons, login, oauth, orders, products, refresh_token, stripe, users
from api.views import UserActivationView

admin.autodiscover()
urlpatterns = []

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [url(r"^__debug__/", include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += [
    #     url(r'^404/', views.custom_404),
    # ]

router = routers.DefaultRouter()
# router.register(r'get-users', UserViewSet)

urlpatterns += [
    # Following api is to create new user
    url(r"^admin/", admin_site.urls),
    # url(r'^', include(router.urls)),
    url(r"^users/login/", refresh_token.SocialAppLoginRefreshTokenView.as_view()),
    url(r"^users/(?P<id>\d+)?/?(?P<app_users>[A-Z_]+)?/?$", users.Users.as_view(), ),
    url(r"^orders/(?P<id>\d+)?/?$", orders.Orders.as_view()),
    url(r"^user_purchase/(?P<type>[a-z_]+)?/?(?P<id>\d+)?/?$", stripe.Cards.as_view(), ),
    url(r"^coupon/", coupons.CouponView.as_view()),
    url(r"^product/(?P<id>\d+)?/?$", products.ProductView.as_view()),
    # Sample api view which is protected by tokenAuthentication
    # url(r'^api-token-auth/', views.obtain_auth_token),
    # following api view which if provided with valid username and
    # password will return token against user, and if token is expired
    # it will return refreshed token.
    url(r"^login/", login.LoginUser.as_view()),
    # url(r'^users/', include('djoser.urls')),
    url(r"^users/logout/", refresh_token.logout_user),
    url(r"^users/activate/?$", UserActivationView.as_view(), name="user-activate"),
    url(r"^auth/", include("rest_framework_social_oauth2.urls")),
    url(r"^o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    url(r"^social-login/", oauth.OAuth.as_view()),
]

urlpatterns += [
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
