from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from billing.serializers.coupons import ApplyCouponResponseSerializer, ApplyCouponSerializer
from billing.services.coupon import CouponService


class ApplyCouponView(GenericAPIView):
    serializer_class = ApplyCouponSerializer
    response_serializer_class = ApplyCouponResponseSerializer

    def post(self, request: Request, *args, **kwargs):
        coupon_serializer = self.serializer_class(
            data=request.data, context={"request": self.request}
        )
        coupon_serializer.is_valid(raise_exception=True)

        coupon = coupon_serializer.validated_data["coupon"]
        invoice = coupon_serializer.validated_data["invoice"]

        holder = CouponService(invoice, coupon)
        invoice = holder.apply_coupon()

        response = self.response_serializer_class(invoice).data

        return Response(response)
