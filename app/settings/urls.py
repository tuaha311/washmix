from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from api.client.views.pdf import generate_client_pdf

import debug_toolbar
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from api.generators import WashMixSchemaGenerator
from api.views import EmailRenderView, static_server
from sms.views import outbound_sms, send_sms
from django.contrib.admin import AdminSite
from django.urls import path
from deliveries.admin import DeliveryAdmin

urlpatterns = []


# CustomAdminURL is used to extend the admin functionality with additional protected URLs.
# These URLs are designed for admin-only access.
class CustomAdminURL(AdminSite):
    def get_urls(self):
        urls = super().get_urls()

        # Add the custom URL patterns
        urls += [
            path("sms/outbound-sms/", self.admin_view(outbound_sms), name="outbound_sms"),
            path("sms/send-sms/", self.admin_view(send_sms), name="send_sms"),
            path("deliveries/update-deliveries/", DeliveryAdmin.update_deliveries, name="update-deliveries"),
            path("client/generate-pdf/", self.admin_view(generate_client_pdf), name="generate-pdf"),
        ]

        return urls

# Register your custom admin site
custom_admin_site = CustomAdminURL(name="custom-admin-url")

schema_view = get_schema_view(
    openapi.Info(
        title="WashMix",
        default_version="v1.0",
        description="WashMix REST API",
    ),
    public=True,
    permission_classes=(),
    generator_class=WashMixSchemaGenerator,
)


if settings.DEBUG:
    local_patterns = [
        # Email render view
        path("render/<str:email_kind>/", EmailRenderView.as_view()),
    ]

    urlpatterns += local_patterns


if settings.SHOW_OPENAPI_SCHEMA:
    local_patterns = [
        # OpenAPI docs
        path(
            "openapi/",
            schema_view.without_ui(cache_timeout=0),
            name="openapi-schema",
        ),
    ]

    urlpatterns += local_patterns


urlpatterns += [
    # REST API
    path("api/", include("api.urls")),
    path("jet/", include("jet.urls", "jet")),
    path("deliveries/", include("deliveries.urls")),
    path("__debug__/", include(debug_toolbar.urls)),
    path("admin/notifications/", include("notifications.urls")),
    path("admin/", admin.site.urls),
    path("sms/", include("sms.urls")),
    # Static files serving
    *static_server(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    *static_server(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
]


# Include your custom admin URLs
urlpatterns += [
    path("admin/", custom_admin_site.urls),  # Change "admin-url" to the desired path
]
