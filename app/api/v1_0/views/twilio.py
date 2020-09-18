from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from api.v1_0.serializers.twilio import TwilioFlexWebhookSerializer
from pickups.services.twilio import TwilioFlexService


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
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data["message"]
        phone = serializer.validated_data["phone"]

        twilio_service = TwilioFlexService(message, phone)

        delivery = twilio_service.create_delivery()
        message = delivery.pretty_pickup_message
        body = {"message": message}

        return Response(data=body, status=HTTP_200_OK)
