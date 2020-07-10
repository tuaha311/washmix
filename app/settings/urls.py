from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path

import debug_toolbar

urlpatterns = []

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
    ]


urlpatterns += [
    # NEW API
    path("api/v1.0/", include("api.v1_0.urls")),
    # LEGACY API
    path("", include("api.legacy.urls")),
]
