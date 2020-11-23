from orders.containers.order import OrderContainer
from orders.models import Order
from subscriptions.containers import SubscriptionContainer
from subscriptions.models import Subscription
from users.models import Client


def get_extra_context(client_id: int, subscription_id: int = None, order_id: int = None, **kwargs):
    context = {**kwargs}

    client = Client.objects.get(id=client_id)
    context["client"] = client

    if subscription_id:
        subscription = Subscription.objects.get(id=subscription_id)
        subscription_container = SubscriptionContainer(subscription)
        context["subscription_container"] = subscription_container

    if order_id:
        order = Order.objects.get(id=order_id)
        order_container = OrderContainer(order)
        context["order_container"] = order_container

    return context
