from functools import partial

from django.conf import settings
from django.db.transaction import atomic

from billing.choices import Kind, Provider, Purpose
from billing.models import Invoice, Transaction
from users.models import Client


def create_transaction(
    client: Client,
    invoice: Invoice,
    amount: int,
    kind: str,
    source=None,
    provider=Provider.STRIPE,
    stripe_id: str = None,
) -> Transaction:
    """
    Common helper that creates transaction.
    """

    if not source or not isinstance(source, dict):
        source = {}

    transaction = Transaction.objects.create(
        client=client,
        invoice=invoice,
        kind=kind,
        provider=provider,
        stripe_id=stripe_id,
        amount=amount,
        source=source,
    )

    return transaction


create_debit = partial(create_transaction, kind=Kind.DEBIT)
create_credit = partial(create_transaction, kind=Kind.CREDIT, provider=Provider.WASHMIX)


def add_credits(client: Client, amount: int, purpose=Provider.CREDIT_BACK) -> Transaction:
    """
    Helper function that creates invoice and transaction for internal credit accrue.
    """

    with atomic():
        invoice = Invoice.objects.create(
            client=client,
            amount=amount,
            discount=settings.DEFAULT_ZERO_DISCOUNT,
            purpose=Purpose.CREDIT,
        )
        transaction = create_debit(
            client=client,
            invoice=invoice,
            amount=amount,
            provider=purpose,
        )

    return transaction
