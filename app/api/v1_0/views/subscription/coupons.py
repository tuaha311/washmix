from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1_0.serializers.coupons import ApplyCouponInvoiceSerializer, ApplyCouponSerializer
from billing.services.coupon_holder import CouponHolder


class ApplyCouponView(GenericAPIView):
    serializer_class = ApplyCouponSerializer
    invoice_serializer_class = ApplyCouponInvoiceSerializer

    def post(self, request: Request, *args, **kwargs):
        coupon_serializer = self.serializer_class(
            data=request.data, context={"request": self.request}
        )
        coupon_serializer.is_valid(raise_exception=True)

        coupon = coupon_serializer.validated_data["coupon"]
        invoice = coupon_serializer.validated_data["invoice"]

        holder = CouponHolder(invoice, coupon)
        invoice = holder.apply_coupon()

        invoice_serializer = self.invoice_serializer_class(invoice)

        return Response(invoice_serializer.data)
