from rest_framework.generics import GenericAPIView, ListAPIView, UpdateAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.permissions import default_pos_permissions
from orders.api.pos.serializers.orders import OrderSerializer
from orders.containers.order import OrderContainer


class OrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = default_pos_permissions

    def get_queryset(self):
        client = self.request.user.client
        order_list = client.order_list.all()

        return [OrderContainer(item) for item in order_list]


class OrderUpdateView(UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = default_pos_permissions

    def get_queryset(self):
        client = self.request.user.client

        return client.order_list.all()

    def get_object(self):
        instance = super().get_object()

        return OrderContainer(instance)


class OrderPrepareView(GenericAPIView):
    pass


class OrderRepeatView(GenericAPIView):
    """
    View for repeating order.
    """

    def post(self, request: Request, *args, **kwargs):
        return Response()
