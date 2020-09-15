from django.conf import settings

from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from api.v1_0.serializers.sms import FlexWebhookSerializer
from pickups.services.sms import FlexService


class FlexWebhookView(GenericAPIView):
    """
    Twilio `Make HTTP Request` widget status logic:
    - 200 or 204 (success)
    - 3xx (redirect)
    - 4xx or 5xx (fail)
    """

    permission_classes = [AllowAny]
    parser_classes = [FormParser, JSONParser]
    serializer_class = FlexWebhookSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=False)

        message = serializer.validated_data["message"]
        contact = serializer.validated_data["contact"]
        datetime = serializer.validated_data["datetime"]

        service = FlexService(message, contact, datetime)
        service_status = service.handle()

        if service_status == settings.SUCCESS:
            status = HTTP_200_OK
        else:
            status = HTTP_400_BAD_REQUEST

        return Response(status=status)
