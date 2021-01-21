from django.views.generic import TemplateView

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers import HealthSerializer
from notifications.context import email_context
from users.models import Client


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
    template_name = "email/signup.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        client = Client.objects.get(pk=2)

        extra_context = {
            "washmix": email_context,
            "client": client,
        }

        return {**context, **extra_context}
