from django.db.transaction import atomic

from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.client.serializers.checkout import (
    WelcomeCheckoutResponseSerializer,
    WelcomeCheckoutSerializer,
)
from billing.services.card import CardService
from billing.services.checkout import WelcomeCheckoutService
from subscriptions.services.subscription import SubscriptionService


class WelcomeCheckoutView(GenericAPIView):
    serializer_class = WelcomeCheckoutSerializer
    response_serializer_class = WelcomeCheckoutResponseSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        invoice = serializer.validated_data["invoice"]
        user = serializer.validated_data["user"]
        raw_address = serializer.validated_data["address"]
        raw_billing_address = serializer.validated_data["billing_address"]

        client = request.user.client
        checkout_service = WelcomeCheckoutService(client, request, invoice)
        card_service = CardService(client, invoice)
        subscription_service = SubscriptionService(client)

        with atomic():
            card_service.save_card_list()

            user = checkout_service.fill_profile(user)
            address = checkout_service.create_main_address(raw_address)
            billing_address = checkout_service.create_billing_address(raw_billing_address)
            checkout_service.charge()

            subscription_service.finalize(invoice)

        response_body = {
            "user": user,
            "address": address,
            "billing_address": billing_address,
        }
        response = self.response_serializer_class(response_body).data

        return Response(response)
