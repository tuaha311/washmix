from rest_framework import serializers

from billing.models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    package = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = Invoice
        fields = [
            "id",
            "card",
            "package",
            "order",
            "coupon",
            "amount",
            "dollar_amount",
            "discount",
            "dollar_discount",
            "basic",
            "dollar_basic",
        ]
        read_only_fields = [
            "coupon",
            "amount",
            "dollar_amount",
            "discount",
            "dollar_discount",
            "basic",
        ]
