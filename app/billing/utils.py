from billing.models import Invoice
from users.models import Client


def get_or_create_invoice(client: Client):
    Invoice.objects.get_or_create()
