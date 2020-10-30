from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.permissions import default_permissions_for_admin
from orders.api.pos.serializers.orders import OrderCheckoutSerializer, OrderSerializer
from orders.services.order import OrderService


class OrderCheckoutView(GenericAPIView):
    serializer_class = OrderCheckoutSerializer
    response_serializer_class = OrderSerializer
    permission_classes = default_permissions_for_admin

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = request.user.client
        request = serializer.validated_data["request"]
        basket = serializer.validated_data["basket"]

        order_service = OrderService(client)
        order_container = order_service.checkout(basket, request)

        response = self.response_serializer_class(order_container).data
        return Response(response)
