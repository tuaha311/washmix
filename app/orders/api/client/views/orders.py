from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.pos.serializers.orders import OrderSerializer
from orders.choices import OrderPaymentChoices
from orders.containers.order import OrderContainer


class OrderListView(ListAPIView):
    """
    View that show list of order.
    """

    serializer_class = OrderSerializer

    def get_queryset(self):
        client = self.request.user.client
        order_list = client.order_list.exclude(payment=OrderPaymentChoices.FAIL)

        return [OrderContainer(item) for item in order_list]


class OrderRepeatView(GenericAPIView):
    """
    View for repeating order.
    """

    def post(self, request: Request, *args, **kwargs):
        return Response()
