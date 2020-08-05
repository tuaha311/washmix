from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.v1_0.serializers.ping import PingSerializer


class PingView(GenericAPIView):
    """
    PUBLIC METHOD.

    Health of service.
    """

    serializer_class = PingSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"})
