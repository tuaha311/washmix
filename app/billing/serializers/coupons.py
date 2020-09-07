from django.conf import settings

from rest_framework import serializers

from api.fields import InvoiceField
from billing.models import Coupon, Invoice, Package


class ApplyCouponSerializer(serializers.Serializer):
    coupon = serializers.SlugRelatedField(slug_field="code", queryset=Coupon.objects.all())
    invoice = InvoiceField()

    def validate_invoice(self, value):
        invoice = value

        if invoice.is_paid:
            raise serializers.ValidationError(
                detail="You already paid this invoice.", code="invoice_already_paid",
            )

        if invoice.subscription.name == settings.PAYC:
            raise serializers.ValidationError(
                detail="You cannot apply coupon to PAYC.", code="no_coupon_for_payc",
            )

        return value


class ApplyCouponInvoiceSerializer(serializers.ModelSerializer):
    subscription = serializers.SlugRelatedField(read_only=True, slug_field="name")
    coupon = serializers.SlugRelatedField(read_only=True, slug_field="code")

    class Meta:
        model = Invoice
        fields = [
            "id",
            "amount",
            "dollar_amount",
            "subscription",
            "coupon",
            "discount",
            "dollar_discount",
            "basic",
            "dollar_basic",
        ]
