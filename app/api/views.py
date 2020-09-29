from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers import HealthSerializer


class HealthView(GenericAPIView):
    """
    PUBLIC METHOD.

    Health of service.
    """

    serializer_class = HealthSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"})
