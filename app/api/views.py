from django.views.generic import TemplateView

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers import HealthSerializer
from notifications.utils import get_extra_context


class HealthView(GenericAPIView):
    """
    PUBLIC METHOD.

    Health of service.
    """

    serializer_class = HealthSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"})


class RenderView(TemplateView):
    email_template_map = {
        "signup": "email/signup.html",
        "subscription": "email/purchase_gold_platinum.html",
        "request": "email/new_request.html",
        "order": "email/new_order.html",
        "payment_client": "email/payment_fail_client.html",
        "payment_admin": "email/payment_fail_admin.html",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        extra_context = get_extra_context(client_id=2, subscription_id=2, request_id=2, order_id=4)

        return {**context, **extra_context}

    def get_template_names(self):
        kwargs = self.kwargs
        email_kind = kwargs["email_kind"]

        template_name = self.email_template_map[email_kind]

        return [template_name]
