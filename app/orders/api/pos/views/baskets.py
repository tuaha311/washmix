from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.authentication import default_pos_authentication
from api.permissions import default_pos_permissions
from orders.api.pos.serializers.basket import (
    BasketChangeItemSerializer,
    BasketSetExtraItemsSerializer,
)
from orders.api.pos.serializers.orders import OrderSerializer
from orders.services.basket import BasketService


class BasketChangeItemView(GenericAPIView):
    serializer_class = BasketChangeItemSerializer
    response_serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = request.user.client
        price = serializer.validated_data["price"]
        count = serializer.validated_data["count"]
        action = serializer.validated_data["action"]

        service = BasketService(client)
        method = getattr(service, f"{action}_item")
        order_container = method(price, count)

        response = self.response_serializer_class(order_container).data

        return Response(response)


class BasketClearView(GenericAPIView):
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def post(self, request: Request, *args, **kwargs):
        client = request.user.client

        service = BasketService(client)
        service.clear_all()

        return Response()


class BasketSetExtraItemsView(GenericAPIView):
    serializer_class = BasketSetExtraItemsSerializer
    response_serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = request.user.client
        extra_items = serializer.validated_data["extra_items"]

        service = BasketService(client)

        order_container = service.set_extra_items(extra_items)
        response = self.response_serializer_class(order_container).data

        return Response(response)


class BasketView(GenericAPIView):
    response_serializer_class = OrderSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def get(self, request: Request, *args, **kwargs):
        client = request.user.client

        service = BasketService(client)
        order_container = service.get_container()

        response = self.response_serializer_class(order_container).data

        return Response(response)
