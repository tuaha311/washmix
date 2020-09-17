from django.conf import settings
from django.utils.timezone import localtime

from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from api.v1_0.serializers.sms import TwilioFlexWebhookSerializer
from pickups.services.sms import TwilioFlexService


class TwilioFlexWebhookView(GenericAPIView):
    """
    Twilio `Make HTTP Request` widget status logic:
    - 200 or 204 (success)
    - 3xx (redirect)
    - 4xx or 5xx (fail)
    """

    permission_classes = [AllowAny]
    parser_classes = [FormParser, JSONParser]
    serializer_class = TwilioFlexWebhookSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=False)

        client = self.request.user.client
        message = serializer.validated_data["message"]
        contact = serializer.validated_data["contact"]
        now = localtime()

        twilio_service = TwilioFlexService(client, message, contact, now)
        service_status = twilio_service.get_status()

        status = HTTP_400_BAD_REQUEST
        message = ""
        body = {"message": message}

        if service_status == settings.SUCCESS:
            status = HTTP_200_OK
            delivery = twilio_service.create_delivery()
            message = delivery.pretty_pickup_message
            body = {"message": message}

        return Response(data=body, status=status)
