from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from core.common_models import Common


class Service(Common):
    """
    Service that our laundry provide.

    For example:
    - Dry clean
    - Press clean
    """

    title = models.CharField(
        verbose_name="title of service",
        max_length=50,
    )
    item_list = models.ManyToManyField(
        "orders.Item",
        verbose_name="items",
        related_name="service_list",
        through="orders.Price",
    )

    class Meta:
        verbose_name = "service"
        verbose_name_plural = "services"

    def __str__(self):
        return self.title


class Price(Common):
    """
    Intermediate model that holds a logic of pricing
    between item and service.

    For example:
    - Dry clean on Pants price is 10$
    - Dry clean on T-shirts price is 5$
    """

    service = models.ForeignKey(
        "orders.Service",
        verbose_name="service",
        related_name="price_list",
        on_delete=models.CASCADE,
    )
    item = models.ForeignKey(
        "orders.Item",
        verbose_name="item",
        related_name="price_list",
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(
        verbose_name="price on this service with this item",
        max_digits=9,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "price"
        verbose_name_plural = "prices"
        unique_together = ("service", "item",)

    def __str__(self):
        return f"{self.service.title} on {self.item.title} = {self.price} $"


class Item(Common):
    """
    Items of our client that we can handle.

    For example:
    - T-shirt
    - Pants
    """

    title = models.CharField(
        verbose_name="title of item",
        max_length=50,
    )
    image = models.ImageField(
        verbose_name="image",
        blank=True,
    )

    class Meta:
        verbose_name = "item"
        verbose_name_plural = "items"

    def __str__(self):
        return self.title


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
        "locations.Address", on_delete=models.CASCADE, related_name="pickup_address_list",
    )
    dropoff_address = models.ForeignKey(
        "locations.Address", on_delete=models.CASCADE, related_name="dropoff_address_list",
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


# TODO новые модели OrderItem (quantity), Cart
# TODO новые модели DeliveryInterval
