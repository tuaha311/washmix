from django.db.transaction import atomic

from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.services.order import OrderService
from subscriptions.api.serializers.choose import (
    SubscriptionChooseResponseSerializer,
    SubscriptionChooseSerializer,
)
from subscriptions.services.subscription import SubscriptionService


class SubscriptionChooseView(GenericAPIView):
    serializer_class = SubscriptionChooseSerializer
    response_serializer_class = SubscriptionChooseResponseSerializer

    def post(self, request: Request, *args, **kwargs):
        package_serializer = self.serializer_class(data=request.data, context={"request": request})
        package_serializer.is_valid(raise_exception=True)

        client = request.user.client
        package = package_serializer.validated_data["package"]

        subscription_service = SubscriptionService(client)
        order_service = OrderService(client)

        with atomic():
            subscription = subscription_service.fill_from_package(package)
            order_service.checkout_subscription(subscription)
            order_container = order_service.container

        response = self.response_serializer_class(order_container).data

        return Response(response)
