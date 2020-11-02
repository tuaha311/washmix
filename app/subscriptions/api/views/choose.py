from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from subscriptions.api.serializers.choose import (
    SubscriptionChooseResponseSerializer,
    SubscriptionChooseSerializer,
)
from subscriptions.services.subscription import SubscriptionService


class SubscriptionChooseView(GenericAPIView):
    serializer_class = SubscriptionChooseSerializer
    response_serializer_class = SubscriptionChooseResponseSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = request.user.client
        package = serializer.validated_data["package"]

        subscription_service = SubscriptionService(client)
        order_container = subscription_service.choose(package)

        response = self.response_serializer_class(order_container).data

        return Response(response)
