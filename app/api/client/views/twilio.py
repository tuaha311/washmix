from django.conf import settings

from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.status import HTTP_200_OK

from api.client.serializers.twilio import (
    TwilioFlexDeliveryWebhookSerializer,
    TwilioFlexOnlineWorkersWebhookSerializer,
)
from deliveries.services.twilio import TwilioFlexService


class TwilioFlexDeliveryWebhookView(GenericAPIView):
    """
    Twilio `Make HTTP Request` widget status logic:
    - 200 or 204 (success)
    - 3xx (redirect)
    - 4xx or 5xx (fail)
    """

    permission_classes = [AllowAny]
    parser_classes = [FormParser, JSONParser]
    serializer_class = TwilioFlexDeliveryWebhookSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data["message"]
        phone = serializer.validated_data["phone"]

        service = TwilioFlexService(message, phone)

        # we are forced to handle error in this way instead of
        # storing all validation logic in serializer, because when
        # Twilio Flex received an 4xx status code it send an SMS / Email to
        # owner with error log (Twilio sees 4xx as a application errors, not just a negative scenario).
        # for this reason, we are sending an 2xx status code and storing all logic in
        # `event` and `code` fields of response body.
        try:
            service.validate_or_save()
            request = service.create_request()
            message = request.pretty_pickup_message
            body = {
                "message": message,
                "event": settings.TWILIO_SUCCESS,
                "code": settings.TWILIO_PICKUP_CODE,
            }
        except ValidationError as e:
            error_detail = e.detail[0]
            body = {
                "message": error_detail,
                "event": settings.TWILIO_FAIL,
                "code": error_detail.code,
            }

        return Response(data=body, status=HTTP_200_OK)


class TwilioFlexOnlineWorkersWebhookView(GenericAPIView):
    """
    Twilio `Make HTTP Request` widget status logic:
    - 200 or 204 (success)
    - 3xx (redirect)
    - 4xx or 5xx (fail)
    """

    permission_classes = [AllowAny]
    parser_classes = [FormParser, JSONParser]
    serializer_class = TwilioFlexOnlineWorkersWebhookSerializer

    def get(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        service = TwilioFlexService()
        sid = settings.TWILIO_WORKSPACE_SID
        is_workers_online = service.is_workers_online(sid)
        body = {"online": is_workers_online}

        return Response(data=body, status=HTTP_200_OK)
