from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1_0.serializers.subscription.packages import (
    SetSubscriptionInvoiceSerializer,
    SetSubscriptionSerializer,
)
from billing.services.subscription_handler import SubscriptionHandler


class SetSubscriptionView(GenericAPIView):
    serializer_class = SetSubscriptionSerializer
    invoice_serializer_class = SetSubscriptionInvoiceSerializer

    def post(self, request: Request, *args, **kwargs):
        package_serializer = self.serializer_class(data=request.data, context={"request": request})
        package_serializer.is_valid(raise_exception=True)

        client = request.user.client
        package = package_serializer.validated_data["package"]

        handler = SubscriptionHandler(client)
        invoice = handler.change(package)

        invoice_serializer = self.invoice_serializer_class(invoice)

        return Response(invoice_serializer.data)
