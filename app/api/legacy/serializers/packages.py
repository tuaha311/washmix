from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Coupon
from modules.enums import PACKAGES, CouponType


class PackageSerializer(serializers.Serializer):
    name = serializers.ChoiceField(choices=[(tag.name, tag.name) for tag in PACKAGES])
    currency = serializers.CharField()
    coupon_code = serializers.CharField(required=False)

    def validate(self, attrs):

        coupon_code = attrs.get("coupon_code")
        if coupon_code:
            profile = self.context["request"].user.profile
            if not profile.is_coupon:
                raise ValidationError(detail="Invalid Coupon code")

            try:
                coupon = Coupon.objects.get(name=coupon_code)
                if not coupon.valid:
                    raise ValidationError(detail="Not a valid coupon anymore")
                if CouponType.PACKAGE.value != coupon.coupon_type:
                    raise ValidationError(detail="Invalid Coupon")
            except Coupon.DoesNotExist:
                raise ValidationError(detail="Invalid Coupon code")

            attrs["coupon"] = coupon
        return attrs
