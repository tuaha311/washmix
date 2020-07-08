from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import CustomSocialAuthentication
from api.serializers.coupons import CouponsSerializer


class CouponView(APIView):
    authentication_classes = (CustomSocialAuthentication,)
    permission_classes = (IsAdminUser,)

    def post(self, request, **kwargs):
        coupon_id = self.process_request(request=request)
        return Response(
            data={"coupon_id": coupon_id}, status=status.HTTP_201_CREATED, content_type="json",
        )

    def patch(self, request, **kwargs):
        coupon_id = self.process_request(request=request, is_partial=True)
        return Response(
            data={"coupon_id": coupon_id}, status=status.HTTP_200_OK, content_type="json",
        )

    def process_request(self, request, is_partial=False):
        coupons = request.data.get("coupon")
        coupon_ser = CouponsSerializer(data=coupons, partial=is_partial)
        coupon_ser.is_valid(raise_exception=True)
        return coupon_ser.save()
