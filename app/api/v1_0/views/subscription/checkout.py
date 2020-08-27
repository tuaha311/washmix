from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1_0.serializers.checkout import CheckoutSerializer
from billing.checkout_helper import CheckoutHelper


class CheckoutView(GenericAPIView):
    serializer_class = CheckoutSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = request.user.client
        helper = CheckoutHelper(client)
        helper.checkout()

        return Response(request.data)
