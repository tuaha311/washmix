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


class POSBasketChangeItemView(GenericAPIView):
    serializer_class = POSBasketChangeItemSerializer
    response_serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]
        client = order.client
        basket = order.basket
        price = serializer.validated_data["price"]
        count = serializer.validated_data["count"]
        action = serializer.validated_data["action"]

        service = BasketService(client)
        method = getattr(service, f"{action}_item")
        method(basket=basket, price=price, count=count)

        order.refresh_from_db()
        order_container = OrderContainer(order)
        response = self.response_serializer_class(order_container).data

        return Response(response)


class POSBasketClearView(GenericAPIView):
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
    serializer_class = POSBasketSetExtraItemsSerializer
    response_serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]
        extra_items = serializer.validated_data["extra_items"]
        client = order.client
        basket = order.basket

        service = BasketService(client)
        service.set_extra_items(basket, extra_items)

        order.refresh_from_db()
        order_container = OrderContainer(order)
        response = self.response_serializer_class(order_container).data

        return Response(response)


class POSBasketView(GenericAPIView):
    serializer_class = POSBasketClearSerializer
    response_serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def get(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.query_params, context={"request": request})
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]

        order_container = OrderContainer(order)
        response = self.response_serializer_class(order_container).data

        return Response(response)
