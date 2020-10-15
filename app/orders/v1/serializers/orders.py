from rest_framework import serializers

from api.fields import InvoiceField
from billing.validators import validate_client_can_pay
from deliveries.models import Delivery
from orders.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = [
            "client",
        ]


class OrderCheckoutSerializer(serializers.Serializer):
    invoice = InvoiceField(validators=[validate_client_can_pay])
    delivery = serializers.PrimaryKeyRelatedField(queryset=Delivery.objects.all())
