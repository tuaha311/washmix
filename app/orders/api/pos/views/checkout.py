from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.authentication import default_pos_authentication
from api.permissions import default_pos_permissions
from orders.api.pos.serializers.orders import OrderSerializer, POSOrderCheckoutSerializer
from orders.services.order import OrderService


class POSOrderCheckoutView(GenericAPIView):
    serializer_class = POSOrderCheckoutSerializer
    response_serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def post(self, drf_request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=drf_request.data, context={"request": drf_request})
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]
        client = order.client
        employee = drf_request.user.employee

        order_service = OrderService(client)
        order_container = order_service.checkout(order)
        order_service.finalize(order, employee)

        response = self.response_serializer_class(order_container).data
        return Response(response)
