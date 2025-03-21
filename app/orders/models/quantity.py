from django.db import models

from core.common_models import Common


class Quantity(Common):
    """
    Service-side entity.

    **Intermediate** model that handles all stuff related to
    storing more than 1 item in basket.

    Reference - https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.ManyToManyField.through

    For example - you can add a 2 T-Shirt among with 5 Pants.
    And quantity info will be stored in Quantity model.
    """

    basket = models.ForeignKey(
        "orders.Basket",
        related_name="quantity_list",
        verbose_name="basket",
        on_delete=models.CASCADE,
    )
    # can be null only after price removing
    price = models.ForeignKey(
        "orders.Price",
        related_name="quantity_list",
        verbose_name="price",
        on_delete=models.SET_NULL,
        null=True,
    )
    count = models.PositiveSmallIntegerField(
        verbose_name="count of exact item",
    )

    class Meta:
        verbose_name = "quantity"
        verbose_name_plural = "quantity"

    def __str__(self):
        price = self.price
        return f"{price.service} on {price.item} x {self.count} qty."
