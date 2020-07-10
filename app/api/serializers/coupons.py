from rest_framework import serializers

from api.fields import EnumField
from core.models import Coupon
from modules.enums import CouponType


class CouponsSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=True)
    percentage_off = serializers.FloatField(required=True)
    amount_off = serializers.FloatField(required=False)
    valid = serializers.BooleanField(required=False)
    coupon_type = EnumField(enum=CouponType, required=True)

    class Meta:
        model = Coupon
        fields = (
            "id",
            "name",
            "percentage_off",
            "amount_off",
            "valid",
            "coupon_type",
        )

    def create(self, validate_data):

        if validate_data.get("id"):
            coupon = Coupon.objects.get(id=validate_data.get("id"))
        else:
            coupon = Coupon.objects.create(name=validate_data.get("name"))
        for name, val in validate_data.items():
            setattr(coupon, name, val)
        coupon.save()

        response = {"coupon_id": coupon.id}
        return response
