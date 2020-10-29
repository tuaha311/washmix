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

        order = serializer.validated_data["order"]

        client = request.user.client

        subscription_service = SubscriptionService(client)
        subscription_service.checkout(order)

        return Response(request.data)
