from django.urls import path

from .views import outbound_sms, send_sms

urlpatterns = [
    path("outbound-sms/", outbound_sms, name="outbound_sms"),
    path("send-sms/", send_sms, name="send_sms"),
]
