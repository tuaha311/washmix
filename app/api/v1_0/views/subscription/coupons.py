from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1_0.serializers.coupons import ApplyCouponSerializer
from billing.coupon_holder import CouponHolder
from billing.models import Coupon


class ApplyCouponView(GenericAPIView):
    serializer_class = ApplyCouponSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)

        client = self.request.user.client
        coupon = Coupon.objects.get(code=serializer.validated_data["code"])

        holder = CouponHolder(client)
        holder.apply_coupon(coupon)

        return Response({})
