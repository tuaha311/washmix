from django.conf import settings

from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1_0.serializers import payments
from billing.stripe_helper import StripeHelper


class CreateIntentView(GenericAPIView):
    serializer_class = payments.CreateIntentSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)

        client = self.request.user.client
        is_save_card = serializer.validated_data["is_save_card"]
        amount = serializer.validated_data["amount"]

        helper = StripeHelper(client)

        if is_save_card:
            intent = helper.create_setup_intent()
        else:
            intent = helper.create_payment_intent(amount=amount)

        return Response({"public_key": settings.STRIPE_PUBLIC_KEY, "secret": intent.client_secret})


class StripeWebhookView(GenericAPIView):
    serializer_class = payments.StripeWebhookSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)

        return Response({})
