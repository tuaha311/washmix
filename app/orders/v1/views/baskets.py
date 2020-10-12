from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.services.basket import BasketService
from orders.v1.serializers.basket import BasketSerializer, ChangeItemSerializer


class ChangeItemView(GenericAPIView):
    serializer_class = ChangeItemSerializer
    response_serializer_class = BasketSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = request.user.client
        price = serializer.validated_data["price"]
        count = serializer.validated_data["count"]
        action = serializer.validated_data["action"]

        service = BasketService(client)
        method = getattr(service, f"{action}_item")
        basket = method(price, count)

        response = self.response_serializer_class(basket).data

        return Response(response)


class ClearView(GenericAPIView):
    def post(self, request: Request, *args, **kwargs):
        client = request.user.client

        service = BasketService(client)
        service.clear_all()

        return Response()


class BasketView(GenericAPIView):
    response_serializer_class = BasketSerializer

    def get(self, request: Request, *args, **kwargs):
        client = request.user.client

        service = BasketService(client)
        basket = service.basket

        response = self.response_serializer_class(basket).data

        return Response(response)
