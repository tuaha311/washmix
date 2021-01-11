from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.services.order import OrderService
from subscriptions.api.serializers.checkout import SubscriptionCheckoutSerializer
from subscriptions.api.serializers.choose import SubscriptionChooseResponseSerializer


class SubscriptionCheckoutView(GenericAPIView):
    serializer_class = SubscriptionCheckoutSerializer
    response_serializer_class = SubscriptionChooseResponseSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]

        client = request.user.client

        order_service = OrderService(client, order)
        order_container = order_service.checkout(order)

        response = self.response_serializer_class(order_container).data

        return Response(response)
