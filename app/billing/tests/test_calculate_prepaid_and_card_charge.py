from unittest.mock import MagicMock, patch

from billing.choices import InvoicePurpose
from billing.services.payments import PaymentService


def test_subscription():
    client = MagicMock()
    client.balance = 30000
    invoice = MagicMock()
    invoice.paid_amount = 400
    invoice.amount_with_discount = 19900
    invoice.purpose = InvoicePurpose.SUBSCRIPTION

    service = PaymentService(client, invoice)
    result = service._calculate_prepaid_and_card_charge()

    # for subscription paid amount doesn't matter
    assert (0, 19900) == result


def test_when_balance_enough_for_invoice():
    client = MagicMock()
    client.balance = 30000
    invoice = MagicMock()
    invoice.paid_amount = 400
    invoice.amount_with_discount = 10000
    invoice.purpose = InvoicePurpose.ORDER

    service = PaymentService(client, invoice)
    result = service._calculate_prepaid_and_card_charge()

    # 400 already paid, we need to charge 9600
    assert (9600, 0) == result


def test_when_balance_not_enough_for_invoice():
    client = MagicMock()
    client.balance = 8000
    invoice = MagicMock()
    invoice.paid_amount = 400
    invoice.amount_with_discount = 10000
    invoice.purpose = InvoicePurpose.ORDER

    service = PaymentService(client, invoice)
    result = service._calculate_prepaid_and_card_charge()

    # 400 already paid, we charge full balance (8000) and rest of invoice from card
    assert (8000, 1600) == result
