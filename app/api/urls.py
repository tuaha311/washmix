from django.urls import include, path

from api import views

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("client/", include("api.client.urls", namespace="client")),
    path("pos/", include("api.pos.urls", namespace="pos")),
]
