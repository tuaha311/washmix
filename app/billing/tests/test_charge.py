from unittest.mock import MagicMock, patch

from django.conf import settings

from billing.choices import InvoicePurpose
from billing.services.payments import PaymentService


@patch("billing.services.payments.atomic")
@patch("billing.services.payments.create_credit")
@patch("billing.services.payments.StripeHelper")
def test_charge_when_balance_enough_for_basket(stripe_class_mock, create_credit_mock, atomic_mock):
    """
    POS positive case:
        - client has any subscription with rest of 30000 balance
        - in basket items for 20000
    """

    client = MagicMock()
    client.balance = 30000

    invoice = MagicMock()
    invoice.paid_amount = 0
    invoice.amount_with_discount = 20000
    invoice.purpose = InvoicePurpose.BASKET
    paid_amount = invoice.amount_with_discount

    service = PaymentService(client, invoice)
    service.charge()

    atomic_mock.assert_called_once()
    create_credit_mock.assert_called_once_with(client=client, invoice=invoice, amount=paid_amount)
    stripe_class_mock.assert_called_once()


@patch("billing.services.payments.SubscriptionService")
@patch("billing.services.payments.Package")
@patch("billing.services.payments.atomic")
@patch("billing.services.payments.create_credit")
@patch("billing.services.payments.StripeHelper")
@patch("billing.services.payments.CardService")
def test_charge_when_balance_not_enough_for_basket_with_enabled_auto_billing(
    card_service_mock,
    stripe_class_mock,
    create_credit_mock,
    atomic_mock,
    package_class_mock,
    subscription_service_class_mock,
):
    """
    POS negative case:
        - client has GOLD or PLATINUM subscription with rest of 10000 balance
        - in basket items for 20000
        - client has `is_auto_billing` option ENABLED
        - doesn't have enough prepaid balance to pay
    """

    subscription = MagicMock()
    subscription.name = settings.GOLD
    client = MagicMock()
    client.balance = 10000
    client.is_auto_billing = True
    client.subscription = subscription

    card = MagicMock()
    card.stripe_id = "spam"
    client.card_list.all.return_value = [card]
    stripe_instance_mock = MagicMock()
    stripe_class_mock.return_value = stripe_instance_mock
    subscription_service_instance_mock = MagicMock()
    subscription_invoice_mock = MagicMock()
    subscription_service_instance_mock.create_invoice.return_value = [subscription_invoice_mock]
    subscription_service_instance_mock.choose.return_value.original.subscription.price = 19900
    subscription_service_class_mock.return_value = subscription_service_instance_mock

    invoice = MagicMock()
    invoice.paid_amount = 0
    invoice.amount_with_discount = 25000
    invoice.purpose = InvoicePurpose.BASKET
    paid_amount = client.balance

    service = PaymentService(client, invoice)
    service.charge()

    assert atomic_mock.call_count == 2
    subscription_service_instance_mock.choose.assert_called_once()
    subscription_service_instance_mock.create_invoice.assert_called_once()
    subscription_service_instance_mock.checkout.assert_called_once()
    package_class_mock.objects.get.assert_called_once_with(name=settings.GOLD)
    create_credit_mock.assert_called_once_with(client=client, invoice=invoice, amount=paid_amount)
    stripe_instance_mock.create_payment_intent.assert_called_once_with(
        payment_method_id=card.stripe_id,
        amount=19900,
        invoice=subscription_invoice_mock,
        purpose=InvoicePurpose.POS,
    )
    card_service_mock.assert_called_once()


@patch("billing.services.payments.atomic")
@patch("billing.services.payments.create_credit")
@patch("billing.services.payments.StripeHelper")
@patch("billing.services.payments.CardService")
def test_charge_when_balance_not_enough_for_basket_with_disabled_auto_billing(
    card_service_mock,
    stripe_class_mock,
    create_credit_mock,
    atomic_mock,
):
    """
    POS negative case:
        - client has GOLD or PLATINUM subscription with rest of 10000 balance
        - in basket items for 25000
        - client has `is_auto_billing` option DISABLED
        - doesn't have enough prepaid balance to pay
    """

    subscription = MagicMock()
    subscription.name = settings.GOLD
    client = MagicMock()
    client.balance = 10000
    client.is_auto_billing = False
    client.subscription = subscription

    card = MagicMock()
    card.stripe_id = "spam"
    client.card_list.all.return_value = [card]
    stripe_instance_mock = MagicMock()
    stripe_class_mock.return_value = stripe_instance_mock

    invoice = MagicMock()
    invoice.paid_amount = 0
    invoice.amount_with_discount = 25000
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


@patch("billing.services.payments.atomic")
@patch("billing.services.payments.StripeHelper")
@patch("billing.services.payments.CardService")
def test_charge_when_subscription_is_none(card_service_mock, stripe_class_mock, atomic_mock):
    """
    Welcome scenario case:
        - new client tries to pass through scenario
        - he want to buy GOLD or PLATINUM subscription
    """

    client = MagicMock()
    client.balance = 0
    client.subscription = None
    client.is_auto_billing = True

    stripe_instance_mock = MagicMock()
    stripe_class_mock.return_value = stripe_instance_mock
    card = MagicMock()
    card.stripe_id = "spam"
    client.card_list.all.return_value = [card]

    invoice = MagicMock()
    invoice.paid_amount = 0
    invoice.purpose = InvoicePurpose.SUBSCRIPTION
    invoice.amount_with_discount = 19900
    unpaid_amount = invoice.amount_with_discount

    service = PaymentService(client, invoice)
    service.charge()

    atomic_mock.assert_called_once()
    stripe_instance_mock.create_payment_intent.assert_called_once_with(
        payment_method_id=card.stripe_id,
        amount=unpaid_amount,
        invoice=invoice,
        purpose=invoice.purpose,
    )
    card_service_mock.assert_called_once()
