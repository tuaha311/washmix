from django.db import models

from core.common_models import Common


class Service(Common):
    """
    Service-side entity.

    Service that our laundry provide.

    For example:
    - Dry clean
    - Press clean
    """

    # many to many field THROUGH Price
    item_list = models.ManyToManyField(
        "orders.Item",
        verbose_name="items",
        related_name="service_list",
        through="orders.Price",
    )

    title = models.CharField(
        verbose_name="title of service",
        max_length=200,
        unique=True,
    )
    image = models.ImageField(
        verbose_name="image",
        blank=True,
    )

    class Meta:
        verbose_name = "service"
        verbose_name_plural = "services"

    def __str__(self):
        return self.title

    @property
    def visible_price_list(self):
        return self.price_list.filter(item__is_visible=True)
