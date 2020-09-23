from django.conf import settings

from rest_framework import serializers

from orders.models import Price, Quantity


class ChangeItemSerializer(serializers.Serializer):
    price = serializers.PrimaryKeyRelatedField(queryset=Price.objects.all())
    count = serializers.IntegerField()
    action = serializers.ChoiceField(choices=settings.BASKET_ACTION_CHOICES)


class ChangeItemResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quantity
        fields = "__all__"
