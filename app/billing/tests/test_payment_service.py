from unittest.mock import MagicMock, patch

from billing.services.payments import PaymentService


@patch("billing.services.payments.StripeHelper")
def test_balance_greater_that_invoice(stripe_helper_mock):
    client = MagicMock()
    client.balance = 30000
    invoice = MagicMock()
    invoice.balance = 19900

    service = PaymentService(client, invoice)
    service.charge()
