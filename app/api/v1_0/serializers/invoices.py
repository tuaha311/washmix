from rest_framework import serializers

from billing.models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "card",
            "package",
            "order",
            "coupon",
        ]
        read_only_fields = [
            "coupon",
        ]
