from django.db.transaction import atomic

from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from billing.serializers.checkout import CheckoutSerializer
from billing.services.checkout import CheckoutService
from billing.services.payments import PaymentService


class CheckoutView(GenericAPIView):
    serializer_class = CheckoutSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        invoice = serializer.validated_data["invoice"]
        user = serializer.validated_data["user"]
        address = serializer.validated_data["address"]
        is_save_card = serializer.validated_data["is_save_card"]

        client = request.user.client
        payment_service = PaymentService(client, invoice)
        checkout_service = CheckoutService(client, request, invoice)

        with atomic():
            payment_service.update_invoice(is_save_card)
            checkout_service.save_card_list()
            checkout_service.fill_profile(user)
            checkout_service.create_address(address)
            checkout_service.charge()

        return Response(request.data)
