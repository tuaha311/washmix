from unittest.mock import MagicMock, patch

from django.conf import settings

from stripe.error import StripeError

from billing.choices import InvoicePurpose, WebhookKind
from billing.services.payments import PaymentService


@patch("billing.services.payments.Package")
@patch("billing.services.payments.SubscriptionService")
@patch("billing.services.payments.atomic")
@patch("billing.services.payments.Invoice")
@patch("billing.services.payments.create_credit")
@patch("billing.services.payments.StripeHelper")
@patch("billing.services.payments.CardService")
def test_charge_subscription_purchase_when_order_is_is_fully_paid(
    card_service_mock,
    stripe_class_mock,
    create_credit_mock,
    invoice_class_mock,
    atomic_mock,
    subscription_service_class_mock,
    package_class_mock,
):
    """
    POS positive case:
        - client has GOLD or PLATINUM subscription with rest of 1800 balance
        - in basket items for 1200
        - client has `is_auto_billing` option ENABLED
        - we should purchase a NEW subscription, because rest of balance is lower than 2000
        - we are able to charge card
    """

    subscription = MagicMock()
    subscription.name = settings.GOLD
    subscription.amount_with_discount = 19900
    client = MagicMock()
    client.balance = 1800
    client.is_auto_billing = True
    client.subscription = subscription

    card = MagicMock()
    card.stripe_id = "spam"
    client.card_list.all.return_value = [card]
    stripe_instance_mock = MagicMock()
    stripe_class_mock.return_value = stripe_instance_mock

    invoice = MagicMock()
    invoice.paid_amount = 0
    invoice.amount_with_discount = 1200
    invoice.purpose = InvoicePurpose.ORDER
    invoice.order.pk = 200

    subscription_invoice = MagicMock()
    subscription_invoice.id = 500
    subscription_invoice.amount_with_discount = 19900
    invoice_class_mock.objects.create.return_value = subscription_invoice

    subscription_service_instance_mock = MagicMock()
    subscription_service_instance_mock.create_invoice.return_value = [subscription_invoice]
    subscription_service_instance_mock.choose.return_value.original.subscription.price = 19900
    subscription_service_class_mock.return_value = subscription_service_instance_mock

    service = PaymentService(client, invoice)
    service.charge()

    is_fully_paid = service.is_fully_paid
    if is_fully_paid:
        service = PaymentService(client, invoice)
        service.charge_subscription_with_auto_billing()

    assert is_fully_paid is True
    assert atomic_mock.call_count == 2
    create_credit_mock.assert_called_once_with(client=client, invoice=invoice, amount=1200)
    stripe_instance_mock.create_payment_intent.assert_called_once_with(
        payment_method_id=card.stripe_id,
        amount=19900,
        metadata={
            "invoice_id": 500,
            "webhook_kind": WebhookKind.SUBSCRIPTION,
            "continue_with_order": None,
        },
    )
    package_class_mock.objects.get.assert_called_once_with(name=settings.GOLD)
    subscription_service_instance_mock.choose.assert_called_once()
    subscription_service_instance_mock.checkout.assert_called_once()
    invoice_class_mock.objects.create.assert_called_once()
    card_service_mock.assert_called_once()


@patch("billing.services.payments.Package")
@patch("billing.services.payments.SubscriptionService")
@patch("billing.services.payments.atomic")
@patch("billing.services.payments.Invoice")
@patch("billing.services.payments.create_credit")
@patch("billing.services.payments.StripeHelper")
@patch("billing.services.payments.CardService")
def test_charge_subscription_purchase_when_order_is_is_fully_paid_with_auto_billing_but_no_card(
    card_service_mock,
    stripe_class_mock,
    create_credit_mock,
    invoice_class_mock,
    atomic_mock,
    subscription_service_class_mock,
    package_class_mock,
):
    """
    POS positive case:
        - client has GOLD or PLATINUM subscription with rest of 1800 balance
        - in basket items for 1200
        - client has `is_auto_billing` option ENABLED
        - we should purchase a NEW subscription, because rest of balance is lower than 2000
        - we are NOT able to charge card, because card not exists
    """

    subscription = MagicMock()
    subscription.name = settings.GOLD
    subscription.amount_with_discount = 19900
    client = MagicMock()
    client.balance = 1800
    client.is_auto_billing = True
    client.subscription = subscription

    client.card_list.all.return_value = []
    stripe_instance_mock = MagicMock()
    stripe_class_mock.return_value = stripe_instance_mock

    invoice = MagicMock()
    invoice.paid_amount = 0
    invoice.amount_with_discount = 1200
    invoice.purpose = InvoicePurpose.ORDER
    invoice.order.pk = 200

    subscription_invoice = MagicMock()
    subscription_invoice.id = 500
    subscription_invoice.amount_with_discount = 19900
    invoice_class_mock.objects.create.return_value = subscription_invoice

    subscription_service_instance_mock = MagicMock()
    subscription_service_instance_mock.create_invoice.return_value = [subscription_invoice]
    subscription_service_instance_mock.choose.return_value.original.subscription.price = 19900
    subscription_service_class_mock.return_value = subscription_service_instance_mock

    service = PaymentService(client, invoice)
    service.charge()

    is_fully_paid = service.is_fully_paid
    if is_fully_paid:
        service = PaymentService(client, invoice)
        service.charge_subscription_with_auto_billing()

    assert is_fully_paid is True
    assert atomic_mock.call_count == 2
    create_credit_mock.assert_called_once_with(client=client, invoice=invoice, amount=1200)
    stripe_instance_mock.create_payment_intent.assert_not_called()
    package_class_mock.objects.get.assert_called_once_with(name=settings.GOLD)
    subscription_service_instance_mock.choose.assert_called_once()
    subscription_service_instance_mock.checkout.assert_called_once()
    invoice_class_mock.objects.create.assert_called_once()
    card_service_mock.assert_not_called()


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
        - we are NOT able to charge card, because card is invalid
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

    is_fully_paid = service.is_fully_paid
    if is_fully_paid:
        service = PaymentService(client, invoice)
        service.charge_subscription_with_auto_billing()

    assert is_fully_paid is False
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
