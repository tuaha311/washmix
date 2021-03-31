from rest_framework import serializers

from deliveries.models import Request
from orders.utils import prepare_order_prefetch_queryset
from users.models import Client


#
# Client application fields
#
class BaseClientField(serializers.PrimaryKeyRelatedField):
    attribute_name = ""

    def get_queryset(self):
        client = self.context["request"].user.client

        attribute_queryset = getattr(client, self.attribute_name)

        return attribute_queryset.all()


class RequestField(BaseClientField):
    attribute_name = "request_list"


class OrderField(BaseClientField):
    attribute_name = "order_list"


class SubscriptionField(BaseClientField):
    attribute_name = "subscription_list"


class BasketField(BaseClientField):
    attribute_name = "basket_list"


#
# POS application fields
#
class POSOrderField(serializers.PrimaryKeyRelatedField):
    queryset = prepare_order_prefetch_queryset().all()


class POSClientField(serializers.PrimaryKeyRelatedField):
    queryset = Client.objects.all()


class POSRequestField(serializers.PrimaryKeyRelatedField):
    queryset = Request.objects.all()
