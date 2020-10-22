from django.db import models

from core.common_models import Common


class Item(Common):
    """
    Employee-side entity.

    Items of our client that we can handle.

    For example:
    - T-shirt
    - Pants
    """

    title = models.CharField(
        verbose_name="title of item",
        max_length=200,
        unique=True,
    )
    image = models.ImageField(
        verbose_name="image",
        blank=True,
    )
    is_visible = models.BooleanField(
        verbose_name="is item visible on landing page",
        default=False,
    )

    class Meta:
        verbose_name = "item"
        verbose_name_plural = "items"

    def __str__(self):
        return self.title
