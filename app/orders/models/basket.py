from django.db import models

from core.common_models import Common
from core.utils import get_dollars


class Basket(Common):
    """
    Basket for your shopping.
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

    @property
    def amount(self) -> int:
        return self._calculate_sum("amount")

    @property
    def dollar_amount(self) -> float:
        return get_dollars(self, "amount")

    @property
    def discount(self) -> int:
        return self._calculate_sum("discount")

    @property
    def dollar_discount(self) -> float:
        return get_dollars(self, "discount")

    @property
    def amount_with_discount(self) -> int:
        return self._calculate_sum("amount_with_discount")

    @property
    def dollar_amount_with_discount(self) -> float:
        return get_dollars(self, "amount_with_discount")

    def _calculate_sum(self, item_attribute_name: str) -> int:
        quantity_list = self.quantity_list.all()
        amount = [getattr(item, item_attribute_name) for item in quantity_list]

        return sum(amount)


