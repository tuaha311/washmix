from rest_framework.generics import GenericAPIView
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response

from api.authentication import default_pos_authentication
from api.permissions import default_pos_permissions
from deliveries.api.pos.serializers import POSRequestUpdateSerializer
from orders.api.pos.serializers.orders import OrderSerializer
from orders.containers.order import OrderContainer


class POSRequestUpdateView(GenericAPIView):
    """
    Method gives ability to update request info in POS.
    """

    serializer_class = POSRequestUpdateSerializer
    response_serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def post(self, drf_request: DRFRequest, *args, **kwargs):
        serializer = self.serializer_class(
            data=drf_request.data, context={"request": drf_request}, partial=True
        )
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]
        request = order.request
        serializer.instance = request
        serializer.save()

        order.refresh_from_db()
        order_container = OrderContainer(order)
        response = self.response_serializer_class(order_container).data

        return Response(response)
