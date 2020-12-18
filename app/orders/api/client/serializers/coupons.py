from django.conf import settings

from rest_framework import serializers

from api.client.serializers.common import CommonContainerSerializer
from api.fields import OrderField
from billing.models import Coupon
from orders.models import Order


class OrderRemoveCouponSerializer(serializers.Serializer):
    order = OrderField()


class OrderApplyCouponSerializer(serializers.Serializer):
    coupon = serializers.SlugRelatedField(slug_field="code", queryset=Coupon.objects.all())
    # at this moment client can have or not to have payment method
    # 1. welcome scenario (no payment method)
    # 2. etc (have payment method)
    order = OrderField()

    def validate_order(self, value):
        order = value
        subscription = order.subscription

        if subscription and subscription.name == settings.PAYC:
            raise serializers.ValidationError(
                detail="You cannot apply coupon to PAYC.",
                code="no_coupon_for_payc",
            )

        return value


class OrderApplyCouponResponseSerializer(CommonContainerSerializer, serializers.ModelSerializer):
    subscription = serializers.SlugRelatedField(read_only=True, slug_field="name")
    coupon = serializers.SlugRelatedField(read_only=True, slug_field="code")

    class Meta:
        model = Order
        fields = [
            "id",
            "subscription",
            "coupon",
            "amount",
            "dollar_amount",
            "discount",
            "dollar_discount",
            "amount_with_discount",
            "dollar_amount_with_discount",
        ]
