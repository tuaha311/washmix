from rest_framework.viewsets import ModelViewSet

from billing.serializers.invoices import InvoiceSerializer


class InvoiceViewSet(ModelViewSet):
    # TODO remove PATCH / PUT methods

    serializer_class = InvoiceSerializer

    def perform_create(self, serializer: InvoiceSerializer):
        client = self.request.user.client

        return serializer.save(client=client)

    def get_queryset(self):
        client = self.request.user.client

        return client.invoice_list.all()
