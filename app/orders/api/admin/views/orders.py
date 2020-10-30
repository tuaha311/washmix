from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.admin.serializers.orders import OrderSerializer
from orders.containers.order import OrderContainer


class OrderListView(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        client = self.request.user.client
        order_list = client.order_list.all()

        return [OrderContainer(item) for item in order_list]


class OrderPrepareView(GenericAPIView):
    pass


class OrderRepeatView(GenericAPIView):
    """
    View for repeating order.
    """

    def post(self, request: Request, *args, **kwargs):
        return Response()
