from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from twilio.twiml.messaging_response import MessagingResponse


class FlexWebhookView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request: Request, *args, **kwargs):
        resp = MessagingResponse()

        resp.message("The Robots are coming! Head for the hills!")

        return Response()
