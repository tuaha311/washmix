from django.conf import settings
from django.db.models import ObjectDoesNotExist

import stripe
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from billing.models import Invoice
from billing.services.invoice import InvoiceService
from billing.services.payments import PaymentService
from billing.v1.serializers import payments
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

        payment_service = PaymentService(client, invoice)

        InvoiceService.update_invoice(invoice, is_save_card)
        intent = payment_service.create_intent()

        response_body = {"public_key": settings.STRIPE_PUBLIC_KEY, "secret": intent.client_secret}
        response = self.response_serializer_class(response_body).data

        return Response(response)


class StripeWebhookView(GenericAPIView):
    permission_classes = [AllowAny]
    enable_ip_check = False

    def post(self, request: Request, *args, **kwargs):
        # we will use Stripe SDK to check validity of event instead
        # of using serializer for this purpose
        raw_payload = request.data
        event = stripe.Event.construct_from(raw_payload, stripe.api_key)

        if self.enable_ip_check:
            ip_address = request.META["HTTP_X_FORWARDED_FOR"]

            # don't allowing other IPs excluding Stripe's IPs
            if ip_address not in settings.STRIPE_WEBHOOK_IP_WHITELIST:
                return Response(data={"ip": ip_address,}, status=403,)

        if event.type not in ["payment_intent.succeeded", "charge.succeeded"]:
            return Response({}, status=HTTP_200_OK)

        try:
            payment = event.data.object
            client = Client.objects.get(stripe_id=payment.customer)
            invoice = Invoice.objects.get(pk=payment.metadata.invoice_id)
        except ObjectDoesNotExist:
            return Response({}, status=HTTP_200_OK)

        service = PaymentService(client, invoice)
        service.confirm(payment)

        return Response({}, status=HTTP_200_OK)
