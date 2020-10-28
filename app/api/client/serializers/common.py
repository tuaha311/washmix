from rest_framework import serializers


class CommonContainerSerializer(serializers.Serializer):
    amount = serializers.ReadOnlyField()
    dollar_amount = serializers.ReadOnlyField()
    discount = serializers.ReadOnlyField()
    dollar_discount = serializers.ReadOnlyField()
    amount_with_discount = serializers.ReadOnlyField()
    dollar_amount_with_discount = serializers.ReadOnlyField()
