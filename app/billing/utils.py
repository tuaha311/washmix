from functools import partial
from math import ceil
from typing import Union

from django.conf import settings
from django.db.transaction import atomic

from billing.choices import InvoiceKind, InvoiceProvider, InvoicePurpose
from billing.models import Invoice, Transaction
from users.models import Client


def create_transaction(
    client: Client,
    invoice: Invoice,
    amount: Union[int, float],
    kind: str,
    source=None,
    provider=InvoiceProvider.STRIPE,
    stripe_id: str = None,
) -> Transaction:
    """
    Common helper that creates transaction.
    """

    if not source or not isinstance(source, dict):
        source = {}

    # in some cases amount can be float - for example, if we have
    # discount 3.5$ from 35$.
    ceil_amount = ceil(amount)

    transaction = Transaction.objects.create(
        client=client,
        invoice=invoice,
        kind=kind,
        provider=provider,
        stripe_id=stripe_id,
        amount=ceil_amount,
        source=source,
    )

    return transaction


create_debit = partial(create_transaction, kind=InvoiceKind.DEBIT)
create_credit = partial(
    create_transaction, kind=InvoiceKind.CREDIT, provider=InvoiceProvider.WASHMIX
)


def add_credits(client: Client, amount: int, provider=InvoiceProvider.CREDIT_BACK) -> Transaction:
    """
    Helper function that creates invoice and transaction for internal credit accrue.
    """

    with atomic():
        invoice = Invoice.objects.create(
            client=client,
            amount=amount,
            discount=settings.DEFAULT_ZERO_DISCOUNT,
            purpose=InvoicePurpose.CREDIT,
        )
        transaction = create_debit(
            client=client,
            invoice=invoice,
            amount=amount,
            provider=provider,
        )

    return transaction


def confirm_debit(client: Client, invoice: Invoice, provider=InvoiceProvider.WASHMIX):
    """
    Function that confirms invoice with desired Transaction kind (debit)
    """

    amount = invoice.amount_with_discount

    transaction = create_debit(
        client=client,
        invoice=invoice,
        amount=amount,
        provider=provider,
    )

    return transaction


def confirm_credit(client: Client, invoice: Invoice, provider=InvoiceProvider.WASHMIX):
    """
    Function that confirms invoice with desired Transaction kind (credit)
    """

    amount = invoice.amount_with_discount

    transaction = create_credit(
        client=client,
        invoice=invoice,
        amount=amount,
        provider=provider,
    )

    return transaction
