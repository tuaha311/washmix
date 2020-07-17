from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from core.common_models import Common


class Order(Common):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="order_list")
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


class Item(Common):
    # TODO изменить на Many To Many
    # TODO добавить количество quantity
    # TODO добавить поле image
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="item_list")
    item = models.TextField(default="")
    cost = models.FloatField(default=0)


# TODO новые модели OrderItem (quantity), Cart
# TODO новые модели DeliveryInterval, Transaction
