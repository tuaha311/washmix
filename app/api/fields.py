from rest_framework import serializers


class InvoiceField(serializers.PrimaryKeyRelatedField):
    """
    Field that provides a `queryset` for Invoice based on Client.
    """

    def get_queryset(self):
        client = self.context["request"].user.client
        return client.invoice_list.all()
