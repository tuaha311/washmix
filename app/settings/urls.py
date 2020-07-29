from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from rest_framework.schemas import get_schema_view
from api.generators import WashMixSchemaGenerator

urlpatterns = []

if settings.DEBUG:
    urlpatterns += [
        # Static files serving
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
        # OpenAPI docs
        path(
            "openapi/",
            get_schema_view(
                title="WashMix",
                description="WashMix REST API",
                version="1.0",
                generator_class=WashMixSchemaGenerator,
                permission_classes=[],
                authentication_classes=[],
            ),
            name="openapi-schema",
        ),
    ]


urlpatterns += [
    # new REST API
    path("api/v1.0/", include("api.v1_0.urls")),
    path("admin/", admin.site.urls),
]
