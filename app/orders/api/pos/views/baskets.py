from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.authentication import default_pos_authentication
from api.permissions import default_pos_permissions
from orders.api.pos.serializers.basket import (
    POSBasketChangeItemSerializer,
    POSBasketClearSerializer,
    POSBasketSetExtraItemsSerializer,
)
from orders.api.pos.serializers.orders import OrderSerializer
from orders.containers.order import OrderContainer
from orders.services.basket import BasketService
from orders.utils import prepare_order_prefetch_queryset


class POSBasketChangeItemView(GenericAPIView):
    """
    Method allows to:
        - Add items to basket
        - Remove items from basket
    """

    serializer_class = POSBasketChangeItemSerializer
    response_serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]
        order_pk = order.pk
        client = order.client
        basket = order.basket
        price = serializer.validated_data["price"]
        count = serializer.validated_data["count"]
        action = serializer.validated_data["action"]

        service = BasketService(client)
        method = getattr(service, f"{action}_item")
        method(basket=basket, price=price, count=count)

        refreshed_order = prepare_order_prefetch_queryset().get(pk=order_pk)
        order_container = OrderContainer(refreshed_order)
        response = self.response_serializer_class(order_container).data

        return Response(response)


class POSBasketClearView(GenericAPIView):
    """
    Method removes all items from basket.
    """

    serializer_class = POSBasketClearSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]
        client = order.client
        basket = order.basket

        service = BasketService(client)
        service.clear_all(basket)

        return Response()


class POSBasketSetExtraItemsView(GenericAPIView):
    """
    Method gives ability to add or remove some extra items to basket.
    """

    serializer_class = POSBasketSetExtraItemsSerializer
    response_serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]
        order_pk = order.pk
        extra_items = serializer.validated_data["extra_items"]
        client = order.client
        basket = order.basket

        service = BasketService(client)
        service.set_extra_items(basket, extra_items)

        refreshed_order = prepare_order_prefetch_queryset().get(pk=order_pk)
        order_container = OrderContainer(refreshed_order)
        response = self.response_serializer_class(order_container).data

        return Response(response)


order_params = openapi.Parameter(
    "order", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True
)


class POSBasketView(GenericAPIView):
    """
    Method allows to see which items inside basket.
    """

    serializer_class = POSBasketClearSerializer
    response_serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions
    is_list_response = False

    @swagger_auto_schema(manual_parameters=[order_params])
    def get(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.query_params, context={"request": request})
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]

        order_container = OrderContainer(order)
        response = self.response_serializer_class(order_container).data

        return Response(response)
