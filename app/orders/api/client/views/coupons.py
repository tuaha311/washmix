from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.client.serializers.coupons import (
    ApplyCouponResponseSerializer,
    ApplyCouponSerializer,
)
from orders.models import Order
from orders.services.order import OrderService


class OrderApplyCouponView(GenericAPIView):
    serializer_class = ApplyCouponSerializer
    response_serializer_class = ApplyCouponResponseSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]
        coupon = serializer.validated_data["coupon"]
        client = self.get_client(order)

        service = OrderService(client)
        order_container = service.apply_coupon(order, coupon)

        response = self.response_serializer_class(order_container).data

        return Response(response)

    def get_client(self, order: Order):
        client = self.request.user.client
        return client
