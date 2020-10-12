from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from orders.services.order import OrderService
from orders.v1.serializers.orders import OrderSerializer


class OrderViewSet(ModelViewSet):
    """
    Methods to manipulate with `Order` entity
    """

    serializer_class = OrderSerializer

    def get_queryset(self):
        client = self.request.user.client
        return client.order_list.all()


class OrderRepeatView(GenericAPIView):
    """
    View for repeating order.
    """

    def post(self, request: Request, *args, **kwargs):
        return Response()


class OrderCheckoutView(GenericAPIView):
    def post(self, request: Request, *args, **kwargs):
        client = request.user.client

        service = OrderService(client)
        service.checkout()

        return Response()
