from functools import partial
from math import ceil
from typing import Optional, Union

from django.conf import settings
from django.db.transaction import atomic

from billing.choices import InvoiceKind, InvoiceProvider, InvoicePurpose, WebhookKind
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


def add_money_to_balance(
    client: Client, amount: int, provider=InvoiceProvider.CREDIT_BACK
) -> Transaction:
    """
    Helper function that creates invoice and transaction in debit direction.
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


def remove_money_from_balance(
    client: Client, amount: int, provider=InvoiceProvider.CREDIT_BACK
) -> Transaction:
    """
    Helper function that creates invoice and transaction in credit direction.
    """

    with atomic():
        invoice = Invoice.objects.create(
            client=client,
            amount=amount,
            discount=settings.DEFAULT_ZERO_DISCOUNT,
            purpose=InvoicePurpose.CREDIT,
        )
        transaction = create_credit(
            client=client,
            invoice=invoice,
            amount=amount,
            provider=provider,
        )

    return transaction


def confirm_debit(
    client: Client, invoice: Invoice, provider=InvoiceProvider.WASHMIX
) -> Transaction:
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


def confirm_credit(
    client: Client, invoice: Invoice, provider=InvoiceProvider.WASHMIX
) -> Transaction:
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


def prepare_stripe_metadata(
    invoice_id: int, webhook_kind: str, continue_with_order: Optional[int]
) -> dict:
    """
    Prepares Stripe's metadata.
    """

    metadata = {
        "invoice_id": invoice_id,
        "webhook_kind": webhook_kind,
        "continue_with_order": continue_with_order,
    }

    return metadata
