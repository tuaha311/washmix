from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.client.serializers.coupons import (
    OrderApplyCouponResponseSerializer,
    OrderApplyCouponSerializer,
    OrderRemoveCouponSerializer,
)
from orders.services.order import OrderService


class OrderApplyCouponView(GenericAPIView):
    serializer_class = OrderApplyCouponSerializer
    response_serializer_class = OrderApplyCouponResponseSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]
        coupon = serializer.validated_data["coupon"]
        client = order.client

        service = OrderService(client)
        order_container = service.apply_coupon(order, coupon)

        response = self.response_serializer_class(order_container).data

        return Response(response)


class OrderRemoveCouponView(GenericAPIView):
    serializer_class = OrderRemoveCouponSerializer
    response_serializer_class = OrderApplyCouponResponseSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]
        client = order.client
        service = OrderService(client)
        order_container = service.remove_coupon(order)

        response = self.response_serializer_class(order_container).data
        return Response(response)
