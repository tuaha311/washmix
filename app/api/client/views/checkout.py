from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.client.serializers.checkout import (
    WelcomeCheckoutResponseSerializer,
    WelcomeCheckoutSerializer,
)
from billing.services.checkout import WelcomeService


class WelcomeCheckoutView(GenericAPIView):
    serializer_class = WelcomeCheckoutSerializer
    response_serializer_class = WelcomeCheckoutResponseSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]
        user = serializer.validated_data["user"]
        raw_address = serializer.validated_data["address"]
        raw_billing_address = serializer.validated_data["billing_address"]

        client = request.user.client
        service = WelcomeService(client, request, order)
        address, billing_address = service.checkout(user, raw_address, raw_billing_address)

        response_body = {
            "user": user,
            "address": address,
            "billing_address": billing_address,
        }
        response = self.response_serializer_class(response_body).data

        return Response(response)
