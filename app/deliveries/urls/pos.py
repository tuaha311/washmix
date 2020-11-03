from django.urls import path

from deliveries.api.pos import views

urlpatterns = [
    path("choose/", views.RequestChooseView.as_view(), name="choose"),
]
