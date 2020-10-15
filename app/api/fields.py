from rest_framework import serializers

from billing.validators import validate_paid_invoice


class InvoiceField(serializers.PrimaryKeyRelatedField):
    """
    Field that provides a `queryset` for Invoice based on Client.
    """

    extra_validators = [validate_paid_invoice]

    def get_queryset(self):
        client = self.context["request"].user.client
        return client.invoice_list.all()

    @property
    def validators(self):
        default_validators = super().validators

        default_validators.extend(self.extra_validators)

        return default_validators
