from django.db.transaction import atomic

from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1_0.serializers.checkout import CheckoutSerializer
from billing.services.checkout import CheckoutService


class CheckoutView(GenericAPIView):
    serializer_class = CheckoutSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        invoice = serializer.validated_data["invoice"]
        user = serializer.validated_data["user"]
        address = serializer.validated_data["address"]

        client = request.user.client
        checkout_service = CheckoutService(client, request)

        with atomic():
            checkout_service.save_card_list()
            checkout_service.fill_profile(user)
            checkout_service.create_address(address)
            payment = checkout_service.charge(invoice)
            checkout_service.checkout(invoice, payment)

        return Response(request.data)
