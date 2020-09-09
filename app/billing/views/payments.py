from django.conf import settings

import stripe
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from billing.models import Invoice
from billing.serializers import payments
from billing.services.checkout import CheckoutService
from billing.services.payments import PaymentService
from core.utils import ip_in_white_list
from users.models import Client


class CreateIntentView(GenericAPIView):
    serializer_class = payments.CreateIntentSerializer
    response_serializer_class = payments.CreateIntentResponseSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)

        client = self.request.user.client
        is_save_card = serializer.validated_data["is_save_card"]
        invoice = serializer.validated_data["invoice"]

        service = PaymentService(client, invoice)
        service.update_invoice(is_save_card)
        intent = service.create_intent()

        response_body = {"public_key": settings.STRIPE_PUBLIC_KEY, "secret": intent.client_secret}
        response = self.response_serializer_class(response_body).data

        return Response(response)


class StripeWebhookView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request: Request, *args, **kwargs):
        ip_address = request.META["HTTP_X_REAL_IP"]

        if not ip_in_white_list(ip_address, settings.STRIPE_WEBHOOK_IP_WHITELIST):
            return Response(status=403)

        # we will use Stripe SDK to check validity of event instead
        # of using serializer for this purpose
        raw_payload = request.data
        event = stripe.Event.construct_from(raw_payload, stripe.api_key)

        if event.type in ["payment_intent.succeeded", "charge.succeeded"]:
            payment = event.data.object
            client = Client.objects.get(stripe_id=payment.customer)
            invoice = Invoice.objects.get(pk=payment.metadata.invoice_id)
            service = CheckoutService(client, request, invoice)
            service.checkout(payment)

        return Response({}, status=HTTP_200_OK)
