from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from core.common_models import Common


class Request(Common):
    """
    Request to pickup order or drop off a order to the client.
    """

    class Meta:
        verbose_name = "pickup request"
        verbose_name_plural = "pickup requests"


class Order(Common):
    """
    Central point of system - where we processing orders and storing all info
    related to the order.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order_list"
    )
    pickup_address = models.ForeignKey(
        "core.Address", on_delete=models.CASCADE, related_name="pickup_address_list",
    )
    dropoff_address = models.ForeignKey(
        "core.Address", on_delete=models.CASCADE, related_name="dropoff_address_list",
    )

    # TODO rename to delivery_day
    next_day_delivery = models.BooleanField(default=False)
    same_day_delivery = models.BooleanField(default=False)

    # TODO переместить в отдельную модель
    # TODO возможно, стоит добавить флаги ежедневной доставки
    pick_up_from_datetime = models.DateTimeField(default=timezone.now)
    pick_up_to_datetime = models.DateTimeField(default=timezone.now)

    # TODO переместить в отдельную модель
    # TODO возможно, стоит добавить флаги ежедневной доставки
    drop_off_from_datetime = models.DateTimeField(default=timezone.now)
    drop_off_to_datetime = models.DateTimeField(default=timezone.now)

    # TODO what a diff
    instructions = models.TextField(blank=True)
    additional_notes = models.TextField(blank=True)

    # TODO move logic to products
    total_cost = models.FloatField(default=0.0)

    # TODO move logic to coupons
    discount_description = models.TextField(blank=True)
    discount_amount = models.FloatField(default=0)

    count = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=False)


class Service(Common):
    class Meta:
        verbose_name = "service"
        verbose_name_plural = "services"


class Item(Common):
    # TODO переименовать на Service
    # TODO изменить на Many To Many
    # TODO добавить количество quantity
    # TODO добавить поле image
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="item_list")
    item = models.TextField(default="")
    cost = models.FloatField(default=0)

    class Meta:
        verbose_name = "item"
        verbose_name_plural = "items"


# TODO новые модели OrderItem (quantity), Cart
# TODO новые модели DeliveryInterval, Transaction
