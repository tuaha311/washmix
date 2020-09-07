from rest_framework import serializers


class InvoiceField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        client = self.context["request"].user.client
        return client.invoice_list.all()
