from unittest.mock import MagicMock, patch

from django.conf import settings

from subscriptions.services.subscription import SubscriptionService


@patch("subscriptions.services.subscription.PaymentService")
@patch("subscriptions.services.subscription.CardService")
def test_payc_subscription(card_service_class_mock, payment_service_class_mock):
    card_service_instance_mock = MagicMock()
    card_service_class_mock.return_value = card_service_instance_mock
    payment_service_instance_mock = MagicMock()
    payment_service_class_mock.return_value = payment_service_instance_mock
    client = MagicMock()
    card = MagicMock()
    client.card_list.first.return_value = card
    invoice = MagicMock()
    subscription = MagicMock()
    client.subscription = None
    subscription.name = settings.PAYC
    invoice.subscription = subscription

    service = SubscriptionService(client)
    service.charge(invoice)

    payment_service_class_mock.assert_called_once_with(client, invoice)
    card_service_class_mock.asssert_called_once_with(client)
    client.card_list.first.assert_called_once()
    card_service_instance_mock.update_main_card.asssert_called_once_with(client, card)
    payment_service_instance_mock.charge.assert_not_called()


@patch("subscriptions.services.subscription.PaymentService")
@patch("subscriptions.services.subscription.CardService")
def test_gold_platinum_subscription(card_service_class_mock, payment_service_class_mock):
    card_service_instance_mock = MagicMock()
    card_service_class_mock.return_value = card_service_instance_mock
    payment_service_instance_mock = MagicMock()
    payment_service_class_mock.return_value = payment_service_instance_mock
    client = MagicMock()
    card = MagicMock()
    client.card_list.first.return_value = card
    invoice = MagicMock()
    subscription = MagicMock()
    client.subscription = None
    invoice.subscription = subscription
    subscription_list = [settings.GOLD, settings.PLATINUM]

    for item in subscription_list:
        subscription.name = item

        service = SubscriptionService(client)
        service.charge(invoice)

    payment_service_class_mock.assert_called_with(client, invoice)
    card_service_class_mock.asssert_called_with(client)
    client.card_list.first.assert_not_called()
    card_service_instance_mock.update_main_card.assert_not_called()
    payment_service_instance_mock.charge.assert_called_with()
