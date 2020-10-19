from django.db.transaction import atomic

from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.services.order import OrderService
from orders.v1.serializers.orders import OrderCheckoutSerializer, OrderSerializer


class OrderListView(ListAPIView):
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
    serializer_class = OrderCheckoutSerializer
    response_serializer_class = OrderSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = request.user.client
        delivery = serializer.validated_data["delivery"]
        basket = serializer.validated_data["basket"]

        order_service = OrderService(client)

        with atomic():
            order, invoice = order_service.checkout(basket, delivery)
            order_service.charge(invoice)

        response = self.response_serializer_class(order).data
        return Response(response)
