from unittest.mock import MagicMock, patch

from django.conf import settings

from subscriptions.services.subscription import SubscriptionService

INVOICE_IS_PAID = True


@patch("subscriptions.services.subscription.atomic")
def test_payc_subscription(atomic_mock):
    client = MagicMock()
    invoice = MagicMock()
    subscription = MagicMock()
    client.subscription = None
    subscription.name = settings.PAYC
    invoice.subscription = subscription
    invoice.is_paid = INVOICE_IS_PAID

    service = SubscriptionService(client)

    service.set_subscription(invoice)

    assert client.subscription.name == settings.PAYC


@patch("subscriptions.services.subscription.atomic")
def test_gold_platinum_subscription(atomic_mock):
    client = MagicMock()
    invoice = MagicMock()
    subscription = MagicMock()
    client.subscription = None
    invoice.subscription = subscription
    invoice.is_paid = INVOICE_IS_PAID
    subscription_list = [settings.GOLD, settings.PLATINUM]

    for item in subscription_list:
        subscription.name = item
        service = SubscriptionService(client)

        service.set_subscription(invoice)

        assert client.subscription.name == item
