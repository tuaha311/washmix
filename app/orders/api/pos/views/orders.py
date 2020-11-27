from rest_framework.generics import GenericAPIView, ListAPIView, UpdateAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.authentication import default_pos_authentication
from api.permissions import default_pos_permissions
from orders.api.pos.serializers.orders import OrderPrepareSerializer, OrderSerializer
from orders.containers.order import OrderContainer


class OrderPrepareView(GenericAPIView):
    serializer_class = OrderPrepareSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        return Response()


class OrderListView(ListAPIView):
    serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def get_queryset(self):
        client = self.request.user.client
        order_list = client.order_list.all()

        return [OrderContainer(item) for item in order_list]


class OrderUpdateView(UpdateAPIView):
    serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def get_queryset(self):
        client = self.request.user.client

        return client.order_list.all()

    def get_object(self):
        instance = super().get_object()

        return OrderContainer(instance)


class OrderRepeatView(GenericAPIView):
    """
    View for repeating order.
    """

    def post(self, request: Request, *args, **kwargs):
        return Response()
