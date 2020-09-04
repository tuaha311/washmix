from django.conf import settings

from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1_0.serializers.payments import SetupIntentSerializer, StripeWebhookSerializer
from billing.stripe_helper import StripeHelper


class SetupIntentView(GenericAPIView):
    serializer_class = SetupIntentSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)

        client = self.request.user.client
        card = serializer.validated_data["card"]

        helper = StripeHelper(client)
        payment_method = helper.get_payment_method(card.stripe_id)
        setup_intent = helper.create_setup_intent(payment_method)

        return Response(
            {"public_key": settings.STRIPE_PUBLIC_KEY, "setup_secret": setup_intent.client_secret}
        )


class StripeWebhookView(GenericAPIView):
    serializer_class = StripeWebhookSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)

        return Response({})
