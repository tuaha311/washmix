from rest_framework import serializers

from api.client.serializers.common import CommonContainerSerializer
from api.fields import POSClientField, POSOrderField, POSRequestField
from billing.models import Coupon
from deliveries.api.pos.serializers import RequestResponseSerializer
from deliveries.models import Request
from locations.models import Address
from orders.api.pos.serializers.basket import BasketSerializer
from orders.choices import OrderPaymentChoices
from orders.models import Order
from users.models import Client


#
# Checkout serializers
#
class OrderSerializer(CommonContainerSerializer, serializers.ModelSerializer):
    basket = BasketSerializer(allow_null=True)
    request = RequestResponseSerializer(allow_null=True)
    subscription = serializers.SlugRelatedField(slug_field="name", read_only=True, allow_null=True)
    coupon = serializers.SlugRelatedField(
        slug_field="code", allow_null=True, queryset=Coupon.objects.all()
    )
    coupon_discount = serializers.ReadOnlyField()
    subscription_discount = serializers.ReadOnlyField()
    credit_back = serializers.ReadOnlyField()
    dollar_credit_back = serializers.ReadOnlyField()
    coupon_discount_type = serializers.ReadOnlyField()
    discount_percent = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            "id",
            "created",
            "basket",
            "request",
            "subscription",
            "status",
            "pretty_status",
            "note",
            "is_save_card",
            "credit_back",
            "dollar_credit_back",
            "amount",
            "dollar_amount",
            "discount",
            "dollar_discount",
            "amount_with_discount",
            "dollar_amount_with_discount",
            "coupon",
            "coupon_discount",
            "subscription_discount",
            "coupon_discount_type",
            "discount_percent",
            "balance_after_purchase",
            "balance_before_purchase",
        ]


class POSOrderCheckoutSerializer(serializers.Serializer):
    order = POSOrderField()

    def validate_order(self, value):
        """
        Here we are preventing duplicate checkout on paid orders.
        """

        order = value

        if order.payment == OrderPaymentChoices.PAID:
            raise serializers.ValidationError(
                detail="Order already paid.",
                code="order_paid",
            )

        return value


#
# Already formed serializers
#
class POSOrderAlreadyFormedSerializer(serializers.Serializer):
    client = POSClientField()
    request = POSRequestField()


class POSOrderAlreadyFormedResponseSerializer(serializers.Serializer):
    formed = serializers.BooleanField()
    order = serializers.PrimaryKeyRelatedField(allow_null=True, read_only=True)


#
# Prepare serializers
#
class POSOrderPrepareSerializer(POSOrderAlreadyFormedSerializer):
    def validate(self, attrs):
        """
        If client doesn't have a subscription - we can't bill him.
        """

        client = attrs["client"]
        request = attrs["request"]

        if not client.subscription:
            raise serializers.ValidationError(
                detail="Client doesn't have a subscription. Not enough info for Order formation.",
                code="client_doesnt_have_subscription",
            )

        if request not in client.request_list.all():
            raise serializers.ValidationError(
                detail="Client doesn't have this request pickup.",
                code="request_pickup_not_found",
            )

        return attrs


class POSOrderPrepareAddressResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "zip_code",
            "address_line_1",
            "address_line_2",
            "has_doorman",
        ]


class POSOrderPrepareClientResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "balance",
            "dollar_balance",
            "billing_address",
            "pretty_billing_address",
            "detergents",
            "starch",
            "no_crease",
            "fabric_softener",
            "fix_tears",
        ]


class POSOrderPrepareRequestResponseSerializer(serializers.ModelSerializer):
    address = POSOrderPrepareAddressResponseSerializer()

    class Meta:
        model = Request
        fields = [
            "id",
            "comment",
            "is_rush",
            "address",
        ]


class POSOrderPrepareResponseSerializer(serializers.ModelSerializer):
    client = POSOrderPrepareClientResponseSerializer()
    request = POSOrderPrepareRequestResponseSerializer()

    class Meta:
        model = Order
        fields = [
            "id",
            "client",
            "request",
        ]
