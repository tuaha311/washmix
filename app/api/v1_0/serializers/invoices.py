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
            "discount",
        ]
        read_only_fields = [
            "coupon",
            "amount",
            "discount",
        ]
