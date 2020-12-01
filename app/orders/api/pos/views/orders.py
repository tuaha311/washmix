from rest_framework.generics import GenericAPIView, ListAPIView, UpdateAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.authentication import default_pos_authentication
from api.permissions import default_pos_permissions
from orders.api.pos.serializers.orders import (
    OrderPrepareResponseSerializer,
    OrderPrepareSerializer,
    OrderSerializer,
)
from orders.containers.order import OrderContainer
from orders.services.order import OrderService


class POSOrderPrepareView(GenericAPIView):
    serializer_class = OrderPrepareSerializer
    response_serializer_class = OrderPrepareResponseSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = serializer.validated_data["client"]
        request = serializer.validated_data["request"]

        service = OrderService(client)
        order = service.prepare(request)

        response = self.response_serializer_class(order).data

        return Response(response)


class POSOrderListView(ListAPIView):
    serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def get_queryset(self):
        client = self.request.user.client
        order_list = client.order_list.all()

        return [OrderContainer(item) for item in order_list]


class POSOrderUpdateView(UpdateAPIView):
    serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def get_queryset(self):
        client = self.request.user.client

        return client.order_list.all()

    def get_object(self):
        instance = super().get_object()

        return OrderContainer(instance)


class POSOrderRepeatView(GenericAPIView):
    """
    View for repeating order.
    """

    def post(self, request: Request, *args, **kwargs):
        return Response()
