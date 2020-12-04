from django.conf import settings
from django.db.transaction import atomic

import stripe
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from billing.api.serializers import payments
from billing.choices import Purpose
from billing.services.intent import IntentService
from billing.services.payments import PaymentService
from billing.services.webhook import StripeWebhookService
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
        order = serializer.validated_data["order"]

        intent_service = IntentService(client)
        intent = intent_service.create_intent(order, is_save_card)

        response_body = {"public_key": settings.STRIPE_PUBLIC_KEY, "secret": intent.client_secret}
        response = self.response_serializer_class(response_body).data

        return Response(response)


class StripeWebhookView(GenericAPIView):
    permission_classes = [AllowAny]
    success_events = ["charge.succeeded"]
    fail_events = ["charge.failed"]

    def post(self, request: Request, *args, **kwargs):
        # we will use Stripe SDK to check validity of event instead
        # of using serializer for this purpose
        raw_payload = request.data
        event = stripe.Event.construct_from(raw_payload, stripe.api_key)
        webhook_service = StripeWebhookService(request, event)

        # we check input data on our business requirements
        # if they are not met - we are terminating processing and returning error
        if not webhook_service.is_valid():
            status = webhook_service.status
            body = webhook_service.body
            return Response(body, status=status)

        payment, client, invoice, purpose = webhook_service.parse()
        order = invoice.order

        payment_service = PaymentService(client, invoice)
        subscription_service = SubscriptionService(client)
        order_service = OrderService(client)

        with atomic():
            if event.type in self.success_events:
                # we are marked our invoice as paid
                payment_service.confirm(payment)

                if purpose == Purpose.SUBSCRIPTION:
                    subscription_service.finalize(order)

                elif purpose == Purpose.BASKET:
                    order_service.finalize(order)

            elif event.type in self.fail_events:
                if purpose == Purpose.SUBSCRIPTION:
                    subscription_service.fail(order)

                elif purpose == Purpose.BASKET:
                    order_service.fail(order)

        return Response({}, status=HTTP_200_OK)
