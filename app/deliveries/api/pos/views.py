from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from deliveries.api.pos.serializers import RequestChooseSerializer
from deliveries.services.requests import RequestService
from orders.api.pos.serializers.orders import OrderSerializer


class RequestChooseView(GenericAPIView):
    serializer_class = RequestChooseSerializer
    response_serializer_class = OrderSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = request.user.client
        request = serializer.validated_data["request"]

        service = RequestService(client)
        order_container = service.choose(request)

        response = self.response_serializer_class(order_container).data

        return Response(response)
