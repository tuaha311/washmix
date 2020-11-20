from unittest.mock import MagicMock, patch

from django.conf import settings

from orders.choices import PaymentChoices
from subscriptions.services.subscription import SubscriptionService


@patch("subscriptions.services.subscription.send_email")
@patch("subscriptions.services.subscription.atomic")
def test_payc_gold_platinum_subscription(atomic_mock, send_email_mock):
    client = MagicMock()
    order = MagicMock()
    subscription = MagicMock()
    client.subscription = None
    order.subscription = subscription
    subscription_list = [settings.PAYC, settings.GOLD, settings.PLATINUM]

    for item in subscription_list:
        subscription.name = item
        service = SubscriptionService(client)

        service.finalize(order)

        assert client.subscription.name == item
        assert order.payment == PaymentChoices.PAID

    send_email_mock.send.assert_called()
