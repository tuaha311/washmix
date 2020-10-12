from django.urls import path

from subscriptions.v1.views import choose

urlpatterns = [
    # 1. please, choose a subscription - we will return Invoice.id and attach subscription to Invoice,
    # also, we store this data between screens.
    path("choose_package/", choose.ChooseView.as_view(), name="choose_package"),
]
