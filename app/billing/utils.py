from functools import partial

from django.db.transaction import atomic

from billing.models import Invoice, Transaction
from users.models import Client


def create_transaction(
    client: Client,
    invoice: Invoice,
    amount: int,
    kind: str,
    source=None,
    provider=Transaction.STRIPE,
    stripe_id: str = None,
) -> Transaction:
    """
    Common helper that creates transaction.
    """

    if not source:
        source = {}

    transaction = Transaction.objects.create(
        invoice=invoice,
        kind=kind,
        provider=provider,
        client=client,
        stripe_id=stripe_id,
        amount=amount,
        source=source,
    )

    return transaction


create_debit = partial(create_transaction, kind=Transaction.DEBIT)
create_credit = partial(create_transaction, kind=Transaction.CREDIT)


def create_credit_back(client: Client, amount: int) -> Transaction:
    """
    Helper function that creates invoice and transaction for credit back
    functionality.
    """

    with atomic():
        invoice = Invoice.objects.create(client=client, amount=amount,)
        transaction = create_debit(
            client=client, invoice=invoice, amount=amount, provider=Transaction.CREDIT_BACK,
        )

    return transaction
