from unittest.mock import MagicMock, patch

from billing.choices import InvoicePurpose
from billing.services.payments import PaymentService


@patch("billing.services.payments.atomic")
@patch("billing.services.payments.create_credit")
@patch("billing.services.payments.StripeHelper")
def test_charge_when_balance_greater_that_invoice(
    stripe_class_mock, create_credit_mock, atomic_mock
):
    client = MagicMock()
    client.balance = 30000
    invoice = MagicMock()
    invoice.paid_amount = 0
    invoice.amount_with_discount = 19900
    paid_amount = invoice.amount_with_discount

    service = PaymentService(client, invoice)
    service.charge()

    atomic_mock.assert_called_once()
    create_credit_mock.assert_called_once_with(client=client, invoice=invoice, amount=paid_amount)
    stripe_class_mock.assert_called_once()


@patch("billing.services.payments.atomic")
@patch("billing.services.payments.create_credit")
@patch("billing.services.payments.StripeHelper")
@patch("billing.services.payments.CardService")
def test_charge_when_balance_not_enough_for_invoice(
    card_service_mock, stripe_class_mock, create_credit_mock, atomic_mock
):
    stripe_instance_mock = MagicMock()
    stripe_class_mock.return_value = stripe_instance_mock
    client = MagicMock()
    client.balance = 10000
    client.is_auto_billing = True
    card = MagicMock()
    card.stripe_id = "spam"
    client.card_list.all.return_value = [card]
    invoice = MagicMock()
    invoice.paid_amount = 0
    invoice.amount_with_discount = 19900
    invoice.purpose = InvoicePurpose.BASKET
    paid_amount = client.balance
    unpaid_amount = invoice.amount_with_discount - client.balance

    service = PaymentService(client, invoice)
    service.charge()

    atomic_mock.assert_called_once()
    create_credit_mock.assert_called_once_with(client=client, invoice=invoice, amount=paid_amount)
    stripe_instance_mock.create_payment_intent.assert_called_once_with(
        payment_method_id=card.stripe_id,
        amount=unpaid_amount,
        invoice=invoice,
        purpose=invoice.purpose,
    )
    card_service_mock.assert_called_once()
