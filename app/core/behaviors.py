from functools import partial

from django.db import models

from core.utils import get_dollars


class Stripeable(models.Model):
    """
    Behavior for model that define default fields
    for Stripe integration.
    """

    stripe_id = models.CharField(
        verbose_name="Stripe ID",
        max_length=100,
        blank=True,
        null=True,
        unique=True,
    )

    class Meta:
        abstract = True


def create_price_class(class_name, attribute_name):
    """
    Here we are using technique called `Metaclasses`.
    Instead of creating multiple similar class with same set of fields,
    we creating a function that creates a class definitions.

    If we call this function with `attribute_name=price` resulting model will have this fields:
    * __module__ (module path)
    * __doc__ (docstring, documentation)
    * price = models.BigIntegerField (field in db)
    * dollar_price (property)
    * Meta (django model settings)

    Also, this class will have an `class Meta` with `abstract = True` - you
    can easily inherit it in model and it will add a field for you.
    """

    class Meta:
        abstract = True

    dollar_propery_name = f"dollar_{attribute_name}"
    attrs = {
        "__doc__": "Behavior that defines amount field in cents.\n"
        "Also, it provides .dollar_amount property\n",
        "__module__": "core.behaviors",
        "Meta": Meta,
        attribute_name: models.BigIntegerField(verbose_name=f"{attribute_name}, in cents (¢)"),
        dollar_propery_name: property(partial(get_dollars, attribute_name=attribute_name)),
    }
    base_classes = (models.Model,)

    return type(class_name, base_classes, attrs)


Amountable = create_price_class("Amountable", "amount")
Priceable = create_price_class("Priceable", "price")
Discountable = create_price_class("Discountable", "discount")
Valuable = create_price_class("Valuable", "value")
