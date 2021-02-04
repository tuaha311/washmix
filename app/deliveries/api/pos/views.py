from rest_framework.generics import GenericAPIView
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response

from api.authentication import default_pos_authentication
from api.permissions import default_pos_permissions
from deliveries.api.pos.serializers import POSRequestRushAmountSerializer
from orders.api.pos.serializers.orders import OrderSerializer
from orders.containers.order import OrderContainer


class POSRequestRushAmountView(GenericAPIView):
    """
    Method gives ability to add or remove some extra items to basket.
    """

    serializer_class = POSRequestRushAmountSerializer
    response_serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def post(self, drf_request: DRFRequest, *args, **kwargs):
        serializer = self.serializer_class(data=drf_request.data, context={"request": drf_request})
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]
        rush_amount = serializer.validated_data["rush_amount"]
        request = order.request

        request.rush_amount = rush_amount
        request.save()

        order.refresh_from_db()
        order_container = OrderContainer(order)
        response = self.response_serializer_class(order_container).data

        return Response(response)
