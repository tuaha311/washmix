from rest_framework import serializers

from billing.validators import validate_paid_invoice
from deliveries.models import Request
from orders.models import Order
from users.models import Client


#
# Client application fields
#
class BaseClientField(serializers.PrimaryKeyRelatedField):
    attribute_name = ""

    def get_queryset(self):
        client = self.context["request"].user.client

        attribute_queryset = getattr(client, self.attribute_name)

        return attribute_queryset.all()


class InvoiceField(BaseClientField):
    attribute_name = "invoice_list"

    def get_validators(self):
        default_validators = super().get_validators()

        default_validators.append(validate_paid_invoice)

        return default_validators


class RequestField(BaseClientField):
    attribute_name = "request_list"


class OrderField(BaseClientField):
    attribute_name = "order_list"


class SubscriptionField(BaseClientField):
    attribute_name = "subscription_list"


class BasketField(BaseClientField):
    attribute_name = "basket_list"


#
# POS application fields
#
class POSOrderField(serializers.PrimaryKeyRelatedField):
    queryset = Order.objects.all()


class POSClientField(serializers.PrimaryKeyRelatedField):
    queryset = Client.objects.all()


class POSRequestField(serializers.PrimaryKeyRelatedField):
    queryset = Request.objects.all()
