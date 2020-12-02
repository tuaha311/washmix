from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework.response import Response

from api.authentication import default_pos_authentication
from api.permissions import default_pos_permissions
from orders.api.pos.serializers.orders import (
    OrderPrepareResponseSerializer,
    OrderPrepareSerializer,
    OrderSerializer,
)
from orders.containers.order import OrderContainer
from orders.models import Order
from orders.services.order import OrderService


class POSOrderPrepareView(GenericAPIView):
    serializer_class = OrderPrepareSerializer
    response_serializer_class = OrderPrepareResponseSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = serializer.validated_data["client"]
        request = serializer.validated_data["request"]

        service = OrderService(client)
        order = service.prepare(request)

        response = self.response_serializer_class(order).data

        return Response(response)


class POSOrderUpdateView(UpdateAPIView):
    """
    Method for order update.
    In most cases it used to change `note`.
    """

    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def get_object(self):
        instance = super().get_object()

        return OrderContainer(instance)
