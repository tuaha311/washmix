from rest_framework.generics import ListAPIView

from billing.v1.serializers.invoices import InvoiceSerializer


class InvoiceListView(ListAPIView):
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        client = self.request.user.client
        return client.invoice_list.all()
