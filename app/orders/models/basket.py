# from django.contrib.postgres.fields import JSONField
from django.db import models

from core.common_models import CommonAmountDiscountModel


class Basket(CommonAmountDiscountModel):
    """
    Employee-side and Client-side entity.

    Basket for your shopping.
    Basket is about items storing.

    Client can add / remove items from basket.
    After shopping, client can create and order and pay invoice.
    """

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        on_delete=models.CASCADE,
        related_name="basket_list",
    )
    # here we are linking with `Price` model instead of
    # `Item` because item relation not enough to form price -
    # only `Price` model has all capabilities to provide full info.
    item_list = models.ManyToManyField(
        "orders.Price",
        verbose_name="items in basket",
        related_name="basket_list",
        through="orders.Quantity",
    )

    extra_items = models.JSONField(
        verbose_name="extra items",
        default=dict,
        blank=True,
    )

    class Meta:
        verbose_name = "basket"
        verbose_name_plural = "baskets"
        ordering = ["-created"]

    def __str__(self):
        return f"Basket # {self.id}"
