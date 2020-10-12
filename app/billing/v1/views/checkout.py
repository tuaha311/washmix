from django.db.transaction import atomic

from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from billing.services.card import CardService
from billing.services.checkout import CheckoutService
from billing.services.payments import PaymentService
from billing.v1.serializers.checkout import WelcomeCheckoutSerializer


class WelcomeCheckoutView(GenericAPIView):
    serializer_class = WelcomeCheckoutSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        invoice = serializer.validated_data["invoice"]
        user = serializer.validated_data["user"]
        raw_address = serializer.validated_data["address"]
        raw_billing_address = serializer.validated_data["billing_address"]
        is_same_address = raw_address == raw_billing_address

        client = request.user.client
        checkout_service = CheckoutService(client, request, invoice)
        payment_service = PaymentService(client, invoice)
        card_service = CardService(client, invoice)

        with atomic():
            card_service.save_card_list()

            checkout_service.fill_profile(user)
            checkout_service.create_main_address(raw_address)
            checkout_service.create_billing_address(raw_billing_address, is_same_address)

            payment_service.charge()

        return Response(request.data)
