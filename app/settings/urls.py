from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path

from rest_framework.schemas import get_schema_view

urlpatterns = []

if settings.DEBUG:
    urlpatterns += [
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
    ]


urlpatterns += [
    # new REST API
    path("api/v1.0/", include("api.v1_0.urls")),
    # OpenAPI docs
    path(
        "openapi/",
        get_schema_view(
            title="WashMix",
            description="WashMix REST API",
            version="1.0",
            authentication_classes=[],
            permission_classes=[],
        ),
        name="openapi-schema",
    ),
    # legacy REST API
    path("", include("api.legacy.urls")),
]
