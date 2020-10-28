from django.db.transaction import atomic

from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.serializers.orders import OrderCheckoutSerializer, OrderSerializer
from orders.containers.order import OrderContainer
from orders.services.order import OrderService


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


class OrderCheckoutView(GenericAPIView):
    serializer_class = OrderCheckoutSerializer
    response_serializer_class = OrderSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = request.user.client
        request = serializer.validated_data["request"]
        basket = serializer.validated_data["basket"]

        order_service = OrderService(client)

        with atomic():
            order, invoice_list = order_service.checkout(basket, request)

            for invoice in invoice_list:
                order_service.charge(invoice)

        order_container = order_service.container
        response = self.response_serializer_class(order_container).data
        return Response(response)
