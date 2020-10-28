from django.db.transaction import atomic

from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from subscriptions.api.serializers.checkout import SubscriptionCheckoutSerializer
from subscriptions.services.subscription import SubscriptionService


class SubscriptionCheckoutView(GenericAPIView):
    serializer_class = SubscriptionCheckoutSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        invoice = serializer.validated_data["invoice"]

        client = request.user.client
        subscription_service = SubscriptionService(client)

        with atomic():
            subscription_service.charge(invoice)
            subscription_service.set_subscription(invoice)

        return Response(request.data)
