from unittest.mock import MagicMock, patch

from django.conf import settings

from stripe.error import StripeError

from billing.choices import InvoicePurpose, WebhookKind
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
    client.subscription.amount_with_discount = 29900

    invoice = MagicMock()
    invoice.paid_amount = 0
    invoice.amount_with_discount = 20000
    invoice.purpose = InvoicePurpose.ORDER

    service = PaymentService(client, invoice)
    service.charge()
    fully_paid = service.fully_paid

    assert fully_paid is True
    atomic_mock.assert_called_once()
    create_credit_mock.assert_called_once_with(client=client, invoice=invoice, amount=20000)
    stripe_class_mock.assert_called_once()


@patch("billing.services.payments.Invoice")
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
    invoice_class_mock,
):
    """
    POS negative case:
        - client has GOLD or PLATINUM subscription with rest of 10000 balance
        - in basket items for 20000
        - client has `is_auto_billing` option ENABLED
        - doesn't have enough prepaid balance to pay
        - we are able to charge card
    """

    subscription = MagicMock()
    subscription.name = settings.GOLD
    subscription.amount_with_discount = 19900
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
    subscription_invoice_mock.id = 100
    subscription_service_instance_mock.create_invoice.return_value = [subscription_invoice_mock]
    subscription_service_instance_mock.choose.return_value.original.subscription.price = 19900
    subscription_service_class_mock.return_value = subscription_service_instance_mock

    invoice = MagicMock()
    invoice.paid_amount = 0
    invoice.amount_with_discount = 25000
    invoice.purpose = InvoicePurpose.ORDER
    invoice.order.pk = 200

    subscription_invoice = MagicMock()
    subscription_invoice.id = 500
    subscription_invoice.amount_with_discount = 19900
    invoice_class_mock.objects.create.return_value = subscription_invoice

    service = PaymentService(client, invoice)
    service.charge()
    fully_paid = service.fully_paid

    assert fully_paid is True
    assert atomic_mock.call_count == 2
    subscription_service_instance_mock.choose.assert_called_once()
    subscription_service_instance_mock.checkout.assert_called_once()
    package_class_mock.objects.get.assert_called_once_with(name=settings.GOLD)
    create_credit_mock.assert_called_once_with(client=client, invoice=invoice, amount=10000)
    stripe_instance_mock.create_payment_intent.assert_called_once_with(
        payment_method_id=card.stripe_id,
        amount=19900,
        metadata={
            "invoice_id": 500,
            "webhook_kind": WebhookKind.SUBSCRIPTION_WITH_CHARGE,
            "continue_with_order": 200,
        },
    )
    invoice_class_mock.objects.create.assert_called_once()
    card_service_mock.assert_called_once()


@patch("billing.services.payments.atomic")
@patch("billing.services.payments.Invoice")
@patch("billing.services.payments.create_credit")
@patch("billing.services.payments.StripeHelper")
@patch("billing.services.payments.CardService")
def test_charge_when_balance_not_enough_for_basket_with_disabled_auto_billing(
    card_service_mock,
    stripe_class_mock,
    create_credit_mock,
    invoice_class_mock,
    atomic_mock,
):
    """
    POS negative case:
        - client has GOLD or PLATINUM subscription with rest of 10000 balance
        - in basket items for 25000
        - client has `is_auto_billing` option DISABLED
        - doesn't have enough prepaid balance to pay
        - we are able to charge card
    """

    subscription = MagicMock()
    subscription.name = settings.GOLD
    subscription.amount_with_discount = 19900
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
    invoice.purpose = InvoicePurpose.ORDER
    invoice.order.pk = 200

    unpaid_amount = invoice.amount_with_discount - client.balance
    refill_invoice = MagicMock()
    refill_invoice.id = 500
    refill_invoice.amount_with_discount = unpaid_amount
    invoice_class_mock.objects.create.return_value = refill_invoice

    service = PaymentService(client, invoice)
    service.charge()
    fully_paid = service.fully_paid

    assert fully_paid is True
    atomic_mock.assert_called_once()
    create_credit_mock.assert_called_once_with(client=client, invoice=invoice, amount=10000)
    stripe_instance_mock.create_payment_intent.assert_called_once_with(
        payment_method_id=card.stripe_id,
        amount=15000,
        metadata={
            "invoice_id": 500,
            "webhook_kind": WebhookKind.REFILL_WITH_CHARGE,
            "continue_with_order": 200,
        },
    )
    invoice_class_mock.objects.create.assert_called_once()
    card_service_mock.assert_called_once()


@patch("billing.services.payments.Invoice")
@patch("billing.services.payments.SubscriptionService")
@patch("billing.services.payments.Package")
@patch("billing.services.payments.atomic")
@patch("billing.services.payments.create_credit")
@patch("billing.services.payments.StripeHelper")
@patch("billing.services.payments.CardService")
def test_charge_when_balance_not_enough_for_basket_and_card_is_invalid(
    card_service_mock,
    stripe_class_mock,
    create_credit_mock,
    atomic_mock,
    package_class_mock,
    subscription_service_class_mock,
    invoice_class_mock,
):
    """
    POS negative case:
        - client has GOLD or PLATINUM subscription with rest of 10000 balance
        - in basket items for 20000
        - client has `is_auto_billing` option ENABLED
        - doesn't have enough prepaid balance to pay
        - we are NOT able to charge card because card is invalid
    """

    subscription = MagicMock()
    subscription.name = settings.GOLD
    subscription.amount_with_discount = 19900
    client = MagicMock()
    client.balance = 10000
    client.is_auto_billing = True
    client.subscription = subscription

    card = MagicMock()
    card.stripe_id = "spam"
    client.card_list.all.return_value = [card]
    stripe_instance_mock = MagicMock()
    stripe_instance_mock.create_payment_intent.side_effect = StripeError("not-enough-funds")
    stripe_class_mock.return_value = stripe_instance_mock
    subscription_service_instance_mock = MagicMock()
    subscription_invoice_mock = MagicMock()
    subscription_invoice_mock.id = 100
    subscription_service_instance_mock.create_invoice.return_value = [subscription_invoice_mock]
    subscription_service_instance_mock.choose.return_value.original.subscription.price = 19900
    subscription_service_class_mock.return_value = subscription_service_instance_mock

    invoice = MagicMock()
    invoice.paid_amount = 0
    invoice.amount_with_discount = 25000
    invoice.purpose = InvoicePurpose.ORDER
    invoice.order.pk = 200

    subscription_invoice = MagicMock()
    subscription_invoice.id = 500
    subscription_invoice.amount_with_discount = 19900
    invoice_class_mock.objects.create.return_value = subscription_invoice

    service = PaymentService(client, invoice)
    service.charge()
    fully_paid = service.fully_paid

    assert fully_paid is False
    assert atomic_mock.call_count == 2
    subscription_service_instance_mock.choose.assert_called_once()
    subscription_service_instance_mock.checkout.assert_called_once()
    package_class_mock.objects.get.assert_called_once_with(name=settings.GOLD)
    create_credit_mock.assert_called_once_with(client=client, invoice=invoice, amount=10000)
    stripe_instance_mock.create_payment_intent.assert_called_once_with(
        payment_method_id=card.stripe_id,
        amount=19900,
        metadata={
            "invoice_id": 500,
            "webhook_kind": WebhookKind.SUBSCRIPTION_WITH_CHARGE,
            "continue_with_order": 200,
        },
    )
    invoice_class_mock.objects.create.assert_called_once()
    card_service_mock.assert_not_called()


@patch("billing.services.payments.Invoice")
@patch("billing.services.payments.SubscriptionService")
@patch("billing.services.payments.Package")
@patch("billing.services.payments.atomic")
@patch("billing.services.payments.create_credit")
@patch("billing.services.payments.StripeHelper")
@patch("billing.services.payments.CardService")
def test_charge_when_balance_not_enough_for_basket_with_enabled_auto_billing_and_subscription_purchase(
    card_service_mock,
    stripe_class_mock,
    create_credit_mock,
    atomic_mock,
    package_class_mock,
    subscription_service_class_mock,
    invoice_class_mock,
):
    """
    POS negative case:
        - client has GOLD or PLATINUM subscription with rest of 10000 balance
        - in basket items for 20000
        - client has `is_auto_billing` option ENABLED
        - doesn't have enough prepaid balance to pay
        - we are able to charge card
    """

    subscription = MagicMock()
    subscription.name = settings.GOLD
    subscription.amount_with_discount = 19900
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
    subscription_invoice_mock.id = 100
    subscription_service_instance_mock.create_invoice.return_value = [subscription_invoice_mock]
    subscription_service_instance_mock.choose.return_value.original.subscription.price = 19900
    subscription_service_class_mock.return_value = subscription_service_instance_mock

    invoice = MagicMock()
    invoice.paid_amount = 0
    invoice.amount_with_discount = 45000
    invoice.purpose = InvoicePurpose.ORDER
    invoice.order.pk = 200

    subscription_invoice = MagicMock()
    subscription_invoice.id = 500
    subscription_invoice.amount_with_discount = 19900
    invoice_class_mock.objects.create.return_value = subscription_invoice

    service = PaymentService(client, invoice)
    service.charge()
    fully_paid = service.fully_paid

    assert fully_paid is True
    assert atomic_mock.call_count == 1
    create_credit_mock.assert_called_once_with(client=client, invoice=invoice, amount=10000)
    stripe_instance_mock.create_payment_intent.assert_called_once_with(
        payment_method_id=card.stripe_id,
        amount=19900,
        metadata={
            "invoice_id": 500,
            "webhook_kind": WebhookKind.REFILL_WITH_CHARGE,
            "continue_with_order": 200,
        },
    )
    invoice_class_mock.objects.create.assert_called_once()
    card_service_mock.assert_called_once()


@patch("billing.services.payments.atomic")
@patch("billing.services.payments.StripeHelper")
@patch("billing.services.payments.CardService")
def test_charge_when_first_subscription_purchase(card_service_mock, stripe_class_mock, atomic_mock):
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
    invoice.id = 300
    invoice.paid_amount = 0
    invoice.purpose = InvoicePurpose.SUBSCRIPTION
    invoice.amount_with_discount = 19900

    service = PaymentService(client, invoice)
    service.charge()
    fully_paid = service.fully_paid

    assert fully_paid is True
    assert atomic_mock.call_count == 1
    stripe_instance_mock.create_payment_intent.assert_called_once_with(
        payment_method_id=card.stripe_id,
        amount=19900,
        metadata={
            "invoice_id": 300,
            "webhook_kind": WebhookKind.SUBSCRIPTION,
            "continue_with_order": None,
        },
    )
    card_service_mock.assert_called_once()


@patch("billing.services.payments.atomic")
@patch("billing.services.payments.StripeHelper")
@patch("billing.services.payments.CardService")
def test_charge_when_subscription_upgrade_to_platinum(
    card_service_mock, stripe_class_mock, atomic_mock
):
    """
    Case:
        - After welcome scenario user already purchased GOLD subscription
        - He want to upgrade on new PLATINUM subscription
    """

    subscription = MagicMock()
    subscription.name = settings.GOLD
    subscription.amount_with_discount = 19900

    client = MagicMock()
    client.balance = 19900
    client.subscription = subscription
    client.is_auto_billing = True

    stripe_instance_mock = MagicMock()
    stripe_class_mock.return_value = stripe_instance_mock
    card = MagicMock()
    card.stripe_id = "spam"
    client.card_list.all.return_value = [card]

    invoice = MagicMock()
    invoice.id = 300
    invoice.paid_amount = 0
    invoice.purpose = InvoicePurpose.SUBSCRIPTION
    invoice.amount_with_discount = 29900

    service = PaymentService(client, invoice)
    service.charge()
    fully_paid = service.fully_paid

    assert fully_paid is True
    assert atomic_mock.call_count == 1
    stripe_instance_mock.create_payment_intent.assert_called_once_with(
        payment_method_id=card.stripe_id,
        amount=29900,
        metadata={
            "invoice_id": 300,
            "webhook_kind": WebhookKind.SUBSCRIPTION,
            "continue_with_order": None,
        },
    )
    card_service_mock.assert_called_once()
