from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from billing.models import Coupon, Invoice


class ApplyCouponSerializer(serializers.Serializer):
    coupon = serializers.SlugRelatedField(slug_field="code", queryset=Coupon.objects.all())
    invoice = serializers.PrimaryKeyRelatedField(queryset=Invoice.objects.all())

    def validate_invoice(self, value):
        client = self.context["request"].user.client

        invoice = get_object_or_404(client.invoice_list.all(), pk=value.pk)

        if invoice.is_paid:
            raise serializers.ValidationError(
                detail="Invoice already paid.", code="invoice_is_paid",
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
