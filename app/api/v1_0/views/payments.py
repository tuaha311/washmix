from django.conf import settings

import stripe
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1_0.serializers.payments import PaymentSerializer


class CreatePaymentsView(GenericAPIView):
    serializer_class = PaymentSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)

        client = self.request.user.client

        customer = stripe.Customer.create(
            email=client.email,
            metadata={"id": client.id},
        )

        integer_amount = int(serializer.validated_data["amount"] * 100)
        payment = stripe.PaymentIntent.create(
            amount=integer_amount,
            currency=serializer.validated_data["currency"],
            customer=customer["id"],
            receipt_email=client.email,
            setup_future_usage="off_session",
        )

        return Response(
            {"public_key": settings.STRIPE_PUBLIC_KEY, "payment_secret": payment.client_secret}
        )


class StripeWebhookView(GenericAPIView):
    pass
