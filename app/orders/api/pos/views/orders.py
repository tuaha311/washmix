from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.authentication import default_pos_authentication
from api.permissions import default_pos_permissions
from deliveries.choices import DeliveryStatus
from deliveries.models.delivery import Delivery
from orders.api.pos.serializers.orders import (
    OrderSerializer,
    POSOrderAlreadyFormedResponseSerializer,
    POSOrderAlreadyFormedSerializer,
    POSOrderPrepareResponseSerializer,
    POSOrderPrepareSerializer,
)
from orders.containers.order import OrderContainer
from orders.services.order import OrderService
from orders.utils import prepare_order_prefetch_queryset


class POSOrderPrepareView(GenericAPIView):
    """
    Method that prepares order - tries to find order with
    existing basket and request.
    """

    serializer_class = POSOrderPrepareSerializer
    response_serializer_class = POSOrderPrepareResponseSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = serializer.validated_data["client"]
        request = serializer.validated_data["request"]

        service = OrderService(client)
        order = service.prepare(request)

        response = self.response_serializer_class(order).data

        return Response(response)


class POSOrderUpdateView(UpdateAPIView):
    """
    Method for order update.
    In most cases it used to change `note`.
    """

    serializer_class = OrderSerializer
    queryset = prepare_order_prefetch_queryset().all()
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def get_object(self):
        instance = super().get_object()

        return OrderContainer(instance)


class POSOrderAlreadyFormedView(GenericAPIView):
    """
    Method that checks order is already formed by employee and
    paid by client. If order is formed - we show a link to the order in admin.
    If not - we show a button `CREATE ORDER` with redirect to POS.
    """

    serializer_class = POSOrderAlreadyFormedSerializer
    response_serializer_class = POSOrderAlreadyFormedResponseSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def get(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.query_params, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = serializer.validated_data["client"]
        request = serializer.validated_data["request"]

        try:
            if request.pickup.status not in [
                DeliveryStatus.ACCEPTED,
                DeliveryStatus.IN_PROGRESS,
                DeliveryStatus.COMPLETED,
            ]:
                return Response(None)
        except Delivery.DoesNotExist:
            return Response(None)

        service = OrderService(client)
        order = service.get_order_by_request(request)
        formed = service.is_formed(order)

        response = self.response_serializer_class({"formed": formed, "order": order}).data
        return Response(response)
