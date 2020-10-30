from django.urls import include, path

from api import views

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("v1.0/", include("api.client.urls", namespace="v1.0")),
    path("client/", include("api.client.urls", namespace="client")),
    path("pos/", include("api.pos.urls", namespace="pos")),
]
