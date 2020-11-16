from unittest.mock import MagicMock, patch

from django.conf import settings

from notifications.context import email_context
from notifications.tasks import send_email


@patch("notifications.tasks.Client")
@patch("notifications.tasks.SendGridSender")
def test_send_email_no_extra_context(send_grid_sender_class_mock, client_class_mock):
    send_grid_instance_mock = MagicMock()
    send_grid_sender_class_mock.return_value = send_grid_instance_mock
    client_instance_mock = MagicMock()
    client_instance_mock.email = "hello@world.com"
    client_class_mock.objects.get.return_value = client_instance_mock

    send_email(
        event=settings.SIGNUP,
        client_id=10,
    )

    send_grid_instance_mock.send.assert_called_once_with(
        recipient_list=["hello@world.com"],
        event=settings.SIGNUP,
        context={
            "client": client_instance_mock,
            "washmix": email_context,
        },
    )


@patch("notifications.utils.SubscriptionContainer")
@patch("notifications.utils.Subscription")
@patch("notifications.tasks.Client")
@patch("notifications.tasks.SendGridSender")
def test_send_email_with_subscription_context(
    send_grid_sender_class_mock,
    client_class_mock,
    subscription_class_mock,
    subscription_container_class_mock,
):
    send_grid_instance_mock = MagicMock()
    send_grid_sender_class_mock.return_value = send_grid_instance_mock
    client_instance_mock = MagicMock()
    client_instance_mock.email = "hello@world.com"
    client_class_mock.objects.get.return_value = client_instance_mock
    subscription_instance_mock = MagicMock()
    subscription_class_mock.objects.get.return_value = subscription_instance_mock
    subscription_container_instance_mock = MagicMock()
    subscription_container_class_mock.return_value = subscription_container_instance_mock

    send_email(
        event=settings.SIGNUP,
        client_id=10,
        extra_context={
            "subscription_id": 100,
        },
    )

    send_grid_instance_mock.send.assert_called_once_with(
        recipient_list=["hello@world.com"],
        event=settings.SIGNUP,
        context={
            "client": client_instance_mock,
            "washmix": email_context,
            "subscription_container": subscription_container_instance_mock,
        },
    )


@patch("notifications.tasks.Client")
@patch("notifications.tasks.SendGridSender")
def test_send_email_with_extra_context(
    send_grid_sender_class_mock,
    client_class_mock,
):
    send_grid_instance_mock = MagicMock()
    send_grid_sender_class_mock.return_value = send_grid_instance_mock
    client_instance_mock = MagicMock()
    client_instance_mock.email = "hello@world.com"
    client_class_mock.objects.get.return_value = client_instance_mock

    send_email(
        event=settings.SIGNUP,
        client_id=10,
        extra_context={
            "foo": 100,
        },
    )

    send_grid_instance_mock.send.assert_called_once_with(
        recipient_list=["hello@world.com"],
        event=settings.SIGNUP,
        context={
            "client": client_instance_mock,
            "washmix": email_context,
            "foo": 100,
        },
    )
