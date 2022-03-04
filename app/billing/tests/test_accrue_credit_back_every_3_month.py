from datetime import datetime
from unittest.mock import MagicMock, patch

from billing.tasks import accrue_credit_back_every_3_month


@patch("billing.tasks.add_money_to_balance")
@patch("billing.tasks.localtime")
@patch("billing.tasks.Client")
def test_signup_is_today(client_class_mock, localtime_mock, add_money_to_balance_mock):
    now = datetime(2021, 5, 4)

    client = MagicMock()
    client.id = 100
    client.created = datetime(2021, 5, 4)
    client.email = ["foo@spam.com"]
    client_class_mock.objects.all.return_value = [client]

    localtime_mock.return_value = now

    accrue_credit_back_every_3_month()

    add_money_to_balance_mock.assert_not_called()


@patch("billing.tasks.add_money_to_balance")
@patch("billing.tasks.localtime")
@patch("billing.tasks.Client")
def test_signup_is_month_ago(client_class_mock, localtime_mock, add_money_to_balance_mock):
    now = datetime(2021, 6, 4)

    client = MagicMock()
    client.id = 100
    client.created = datetime(2021, 5, 4)
    client.email = ["foo@spam.com"]
    client_class_mock.objects.all.return_value = [client]

    localtime_mock.return_value = now

    accrue_credit_back_every_3_month()

    add_money_to_balance_mock.assert_not_called()


@patch("billing.tasks.exists_in_execution_cache")
@patch("billing.tasks.add_money_to_balance")
@patch("billing.tasks.localtime")
@patch("billing.tasks.Client")
def test_task_is_already_executed(
    client_class_mock, localtime_mock, add_money_to_balance_mock, exists_in_execution_cache_mock
):
    now = datetime(2021, 8, 2)

    client = MagicMock()
    client.id = 100
    client.pk = 100
    client.created = datetime(2021, 5, 4)
    client.email = ["foo@spam.com"]
    client_class_mock.objects.all.return_value = [client]

    localtime_mock.return_value = now

    exists_in_execution_cache_mock.return_value = True

    accrue_credit_back_every_3_month()

    add_money_to_balance_mock.assert_not_called()
    exists_in_execution_cache_mock.assert_called_once_with("credit_back_for_client:100")


@patch("billing.tasks.OrderContainer")
@patch("billing.tasks.exists_in_execution_cache")
@patch("billing.tasks.add_money_to_balance")
@patch("billing.tasks.localtime")
@patch("billing.tasks.Client")
def test_client_doesnt_have_credit_back(
    client_class_mock,
    localtime_mock,
    add_money_to_balance_mock,
    exists_in_execution_cache_mock,
    order_container_class_mock,
):
    now = datetime(2021, 8, 2)

    order = MagicMock()
    order_container_mock = MagicMock()
    order_container_mock.credit_back = 0
    order_container_class_mock.return_value = order_container_mock

    client = MagicMock()
    client.id = 100
    client.pk = 100
    client.created = datetime(2021, 5, 4)
    client.email = ["foo@spam.com"]
    client.order_list.filter.return_value = [order]
    client_class_mock.objects.all.return_value = [client]

    localtime_mock.return_value = now

    exists_in_execution_cache_mock.return_value = False

    accrue_credit_back_every_3_month()

    order_container_class_mock.assert_called_once_with(order)
    add_money_to_balance_mock.assert_not_called()
    exists_in_execution_cache_mock.assert_called_once_with("credit_back_for_client:100")


@patch("billing.tasks.add_to_execution_cache")
@patch("billing.tasks.send_email")
@patch("billing.tasks.OrderContainer")
@patch("billing.tasks.exists_in_execution_cache")
@patch("billing.tasks.add_money_to_balance")
@patch("billing.tasks.localtime")
@patch("billing.tasks.Client")
def test_client_has_credit_back(
    client_class_mock,
    localtime_mock,
    add_money_to_balance_mock,
    exists_in_execution_cache_mock,
    order_container_class_mock,
    send_email_mock,
    add_to_execution_cache_mock,
):
    now = datetime(2021, 8, 2)
    key = "credit_back_for_client:100"

    total_credit_back = 100
    order = MagicMock()
    order_container_mock = MagicMock()
    order_container_mock.credit_back = total_credit_back
    order_container_class_mock.return_value = order_container_mock

    client = MagicMock()
    client.id = 100
    client.pk = 100
    client.created = datetime(2021, 5, 4)
    client.email = ["foo@spam.com"]
    client.order_list.filter.return_value = [order]
    client_class_mock.objects.all.return_value = [client]

    localtime_mock.return_value = now

    exists_in_execution_cache_mock.return_value = False

    accrue_credit_back_every_3_month()

    order_container_class_mock.assert_called_once_with(order)
    add_money_to_balance_mock.assert_called_once_with(
        client, total_credit_back, note="Credit Back by WashMix"
    )
    exists_in_execution_cache_mock.assert_called_once_with(key)
    send_email_mock.send.assert_called_once()
    add_to_execution_cache_mock.assert_called_once_with(key)
