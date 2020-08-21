from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from billing.models import Coupon


class ApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate_code(self, value):
        get_object_or_404(Coupon, code=value)

        return value
