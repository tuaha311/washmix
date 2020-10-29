from rest_framework import serializers

from billing.validators import validate_paid_invoice


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


class BasketField(BaseClientField):
    attribute_name = "basket_list"
