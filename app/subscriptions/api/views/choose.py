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
        package_serializer = self.serializer_class(data=request.data, context={"request": request})
        package_serializer.is_valid(raise_exception=True)

        client = request.user.client
        package = package_serializer.validated_data["package"]

        service = SubscriptionService(client)
        invoice = service.clone_from_package(package)

        response = self.response_serializer_class(invoice).data

        return Response(response)
