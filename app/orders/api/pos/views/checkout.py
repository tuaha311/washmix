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

    def post(self, drf_request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=drf_request.data, context={"request": drf_request})
        serializer.is_valid(raise_exception=True)

        client = drf_request.user.client
        order = serializer.validated_data["order"]

        order_service = OrderService(client)
        order_container = order_service.checkout(order)

        response = self.response_serializer_class(order_container).data
        return Response(response)
