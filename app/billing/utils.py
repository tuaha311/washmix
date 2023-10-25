from functools import partial
from math import ceil
from typing import Optional, Union

from django.conf import settings
from django.db.transaction import atomic

from billing.choices import InvoiceKind, InvoiceProvider, InvoicePurpose
from billing.models import Invoice, Transaction
from core.utils import clone_from_to
from orders.choices import OrderPaymentChoices
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


def add_money_to_balance(
    client: Client, amount: int, provider=InvoiceProvider.CREDIT_BACK, note=None
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
        Order.objects.create(
            client=client,
            invoice=invoice,
            payment=OrderPaymentChoices.PAID,
            balance_before_purchase=client.balance,
            balance_after_purchase=client.balance + amount,
            note=note,
        )
        transaction = create_debit(
            client=client,
            invoice=invoice,
            amount=amount,
            provider=provider,
        )
    print("transaction transaction", transaction)
    return transaction


def remove_money_from_balance(
    client: Client, amount: int, provider=InvoiceProvider.CREDIT_BACK, note=None
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
        Order.objects.create(
            client=client,
            invoice=invoice,
            payment=OrderPaymentChoices.PAID,
            balance_before_purchase=client.balance,
            balance_after_purchase=client.balance - amount,
            note=note,
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


def perform_refund(invoice: Invoice):
    """
    Helper function that performs refund:
        - Creates Invoice with REFUND purpose.
        - Clones all Transactions from original Invoice with reverted `.kind` field.
    """

    common_exclude_fields = [
        "id",
        "created",
        "changed",
    ]
    exclude_fields_of_invoice = [*common_exclude_fields, "transaction_list", "order"]

    with atomic():
        # 1. let's clone an invoice
        cloned_invoice = Invoice()

        clone_from_to(invoice, cloned_invoice, exclude_fields_of_invoice)

        cloned_invoice.purpose = InvoicePurpose.REFUND
        cloned_invoice.save()

        # 2. then we are cloning all transaction list
        for transaction in invoice.transaction_list.all():
            cloned_transaction = Transaction()

            clone_from_to(transaction, cloned_transaction, common_exclude_fields)

            cloned_transaction.invoice = cloned_invoice
            kind = InvoiceKind.DEBIT
            if transaction.kind == InvoiceKind.DEBIT:
                kind = InvoiceKind.CREDIT
            cloned_transaction.kind = kind

            cloned_transaction.save()


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
