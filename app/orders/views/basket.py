from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.serializers.basket import ChangeSerializer
from orders.services.basket import BasketService


class ChangeView(GenericAPIView):
    serializer_class = ChangeSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = request.user.client
        price = serializer.validated_data["price"]
        count = serializer.validated_data["count"]
        action = serializer.validated_data["action"]

        service = BasketService(client)
        method = getattr(service, f"{action}_item")
        method(price, count)

        return Response()


class ClearView(GenericAPIView):
    serializer_class = ChangeSerializer

    def post(self, request: Request, *args, **kwargs):
        package_serializer = self.serializer_class(data=request.data, context={"request": request})
        package_serializer.is_valid(raise_exception=True)

        client = request.user.client
        price = package_serializer.validated_data["price"]

        service = BasketService(client)
        service.clear_all()

        return Response()


class CheckoutView(GenericAPIView):
    serializer_class = ChangeSerializer

    def post(self, request: Request, *args, **kwargs):
        package_serializer = self.serializer_class(data=request.data, context={"request": request})
        package_serializer.is_valid(raise_exception=True)

        client = request.user.client
        price = package_serializer.validated_data["price"]

        service = BasketService(client)
        service.checkout()

        return Response()
