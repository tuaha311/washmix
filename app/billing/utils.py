from functools import partial
from math import ceil
from typing import Optional, Union

from django.conf import settings
from django.db.models import QuerySet, Sum
from django.db.transaction import atomic

from billing.choices import InvoiceKind, InvoiceProvider, InvoicePurpose, WebhookKind
from billing.models import Invoice, Transaction
from orders.models import Order
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


def get_webhook_kind(invoice: Invoice) -> str:
    """
    Get webhook kind based on invoice.
    """

    webhook_kind = WebhookKind.REFILL_WITH_CHARGE

    # for subscription we are always set corresponding webhook kind
    if invoice.purpose == InvoicePurpose.SUBSCRIPTION:
        webhook_kind = WebhookKind.SUBSCRIPTION

    return webhook_kind


def aggregate_invoice_list(invoice_list: QuerySet, order: Order) -> Invoice:
    """
    Aggregates list of Invoices into one with total amount and discount.
    """

    first_invoice = invoice_list.first()
    client = first_invoice.client
    amount = invoice_list.aggregate(total=Sum("amount"))["total"] or 0
    discount = invoice_list.aggregate(total=Sum("discount"))["total"] or 0

    invoice = Invoice.objects.create(
        client=client,
        order=order,
        discount=discount,
        amount=amount,
        purpose=InvoicePurpose.ONE_TIME_PAYMENT,
    )

    return invoice
