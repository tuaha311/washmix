from django.conf import settings
from django.db.transaction import atomic

import stripe
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from billing.choices import Purpose
from billing.models import Invoice
from billing.services.invoice import InvoiceService
from billing.services.payments import PaymentService
from billing.services.webhook import StripeWebhookService
from billing.v1.serializers import payments
from orders.services.order import OrderService
from subscriptions.services.subscription import SubscriptionService


class CreateIntentView(GenericAPIView):
    serializer_class = payments.CreateIntentSerializer
    response_serializer_class = payments.CreateIntentResponseSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)

        client = self.request.user.client
        is_save_card = serializer.validated_data["is_save_card"]
        invoice = serializer.validated_data["invoice"]

        payment_service = PaymentService(client, invoice)

        InvoiceService.update_invoice(invoice, is_save_card)
        intent = payment_service.create_intent()

        response_body = {"public_key": settings.STRIPE_PUBLIC_KEY, "secret": intent.client_secret}
        response = self.response_serializer_class(response_body).data

        return Response(response)


class StripeWebhookView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request: Request, *args, **kwargs):
        # we will use Stripe SDK to check validity of event instead
        # of using serializer for this purpose
        raw_payload = request.data
        event = stripe.Event.construct_from(raw_payload, stripe.api_key)
        webhook_service = StripeWebhookService(request, event)

        if not webhook_service.is_valid():
            status = webhook_service.status
            body = webhook_service.body
            return Response(body, status=status)

        payment, client, invoice, purpose = webhook_service.parse()

        payment_service = PaymentService(client, invoice)
        subscription_service = SubscriptionService(client)
        order_service = OrderService(client)

        with atomic():
            # we are marked our invoice as paid
            payment_service.confirm(payment)

            if purpose == Purpose.SUBSCRIPTION:
                subscription_service.set_subscription(invoice)

            elif purpose == Purpose.BASKET:
                order_service.process()

        return Response({}, status=HTTP_200_OK)
