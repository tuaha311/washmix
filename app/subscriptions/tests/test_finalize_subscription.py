from unittest.mock import MagicMock, patch

from django.conf import settings

from orders.choices import OrderPaymentChoices
from subscriptions.services.subscription import SubscriptionService


@patch("subscriptions.services.subscription.send_email")
@patch("subscriptions.services.subscription.atomic")
def test_payc_gold_platinum_subscription(atomic_mock, send_email_mock):
    client = MagicMock()
    subscription = MagicMock()
    client.subscription = None
    subscription_list = [settings.PAYC, settings.GOLD, settings.PLATINUM]

    for item in subscription_list:
        order = MagicMock()
        invoice = MagicMock()
        invoice.is_paid = True
        invoice.discount = 0
        order.invoice = invoice
        order.subscription = subscription
        order.payment = OrderPaymentChoices.UNPAID

        subscription.name = item

        service = SubscriptionService(client)
        service.finalize(order)

        assert client.subscription.name == item
        assert order.payment == OrderPaymentChoices.PAID
        order.save.assert_called_once()

    send_email_mock.send.assert_called()
