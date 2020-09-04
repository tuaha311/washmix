from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1_0.serializers.checkout import CheckoutSerializer
from billing.services.checkout import CheckoutService
from billing.stripe_helper import StripeHelper


class CheckoutView(GenericAPIView):
    serializer_class = CheckoutSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = request.user.client
        card = client.main_card
        checkout_service = CheckoutService(client, request)
        stripe_helper = StripeHelper(client)
        payment_method = stripe_helper.get_payment_method(card.stripe_id)

        invoice = serializer.validated_data["invoice"]
        user = serializer.validated_data["user"]
        address = serializer.validated_data["address"]

        payment = stripe_helper.create_payment_intent(
            payment_method=payment_method, amount=invoice.amount,
        )

        profile = checkout_service.fill_profile(user)
        address = checkout_service.create_address(address)
        transaction = checkout_service.checkout(invoice, payment, card)

        return Response(request.data)
