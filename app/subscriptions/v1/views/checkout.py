from django.db.transaction import atomic

from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from billing.services.card import CardService
from billing.services.payments import PaymentService
from subscriptions.services.subscription import SubscriptionService
from subscriptions.v1.serializers.checkout import SubscriptionCheckoutSerializer


class SubscriptionCheckoutView(GenericAPIView):
    serializer_class = SubscriptionCheckoutSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        invoice = serializer.validated_data["invoice"]

        client = request.user.client
        payment_service = PaymentService(client, invoice)
        card_service = CardService(client, invoice)
        subscription_service = SubscriptionService(client)

        with atomic():
            card_service.save_card_list()

            payment_service.charge()

            subscription_service.set_subscription(invoice)

        return Response(request.data)
