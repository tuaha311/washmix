from rest_framework import serializers

from billing.models import Invoice
from subscriptions.models import Package


class ChooseSerializer(serializers.Serializer):
    package = serializers.SlugRelatedField(slug_field="name", queryset=Package.objects.all(),)


class ChooseResponseSerializer(serializers.ModelSerializer):
    subscription = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = Invoice
        fields = [
            "id",
            "amount",
            "dollar_amount",
            "subscription",
            "discount",
            "dollar_discount",
            "basic",
            "dollar_basic",
        ]
