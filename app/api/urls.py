from django.urls import include, path

from api import views

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("v1.0/", include("api.v1_0.urls")),
]
