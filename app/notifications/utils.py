from subscriptions.containers import SubscriptionContainer
from subscriptions.models import Subscription


def get_extra_context(subscription_id: int = None, **kwargs):
    context = {**kwargs}

    if subscription_id:
        subscription = Subscription.objects.get(id=subscription_id)
        subscription_container = SubscriptionContainer(subscription)
        context["subscription_container"] = subscription_container

    return context
