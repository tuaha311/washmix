from django.db.transaction import atomic

from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from billing.services.payments import PaymentService
from orders.services.order import OrderService
from orders.v1.serializers.orders import OrderCheckoutSerializer, OrderSerializer


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
    serializer_class = OrderCheckoutSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = request.user.client
        invoice = serializer.validated_data["invoice"]

        payment_service = PaymentService(client, invoice)
        order_service = OrderService(client, invoice)

        with atomic():
            payment_service.charge()

            order_service.checkout()

        return Response()
