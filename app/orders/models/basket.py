from django.db import models

from core.common_models import Common


class Basket(Common):
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

    class Meta:
        verbose_name = "basket"
        verbose_name_plural = "baskets"
