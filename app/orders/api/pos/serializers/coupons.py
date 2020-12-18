from django.conf import settings

from rest_framework import serializers

from api.fields import POSOrderField
from billing.models import Coupon


class POSOrderRemoveCouponSerializer(serializers.Serializer):
    order = POSOrderField()


class POSOrderApplyCouponSerializer(serializers.Serializer):
    coupon = serializers.SlugRelatedField(slug_field="code", queryset=Coupon.objects.all())
    order = POSOrderField()

    def validate_order(self, value):
        order = value
        subscription = order.subscription

        if subscription and subscription.name == settings.PAYC:
            raise serializers.ValidationError(
                detail="You cannot apply coupon to PAYC.",
                code="no_coupon_for_payc",
            )

        return value
