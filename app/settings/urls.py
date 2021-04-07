from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from api.generators import WashMixSchemaGenerator
from api.views import EmailRenderView, static_server

urlpatterns = []

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
    path("admin/", admin.site.urls),
    # Static files serving
    *static_server(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    *static_server(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
]
