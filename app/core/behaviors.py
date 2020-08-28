from django.conf import settings
from django.db import models


class Stripeable(models.Model):
    """
    Behavior for model that define default fields
    for Stripe integration.
    """

    stripe_id = models.CharField(
        verbose_name="Stripe ID", max_length=100, blank=True, null=True, unique=True,
    )

    class Meta:
        abstract = True


def create_price_class(class_name, attribute_name):
    """
    This function helps us to create similar fields with different names.
    We create one field and one property for this field.

    Also, this class will have an `class Meta` with `abstract = True` - you
    can easily inherit it in model.
    """

    class Meta:
        abstract = True

    def get_amount(self):
        amount_value = getattr(self, attribute_name)
        return amount_value / settings.CENTS_IN_DOLLAR

    dollar_propery_name = f"dollar_{attribute_name}"
    attrs = {
        "__doc__": "Behavior that defines amount field in cents.\n"
        "Also, it provides .dollar_amount property\n",
        "__module__": "core.behaviors",
        "Meta": Meta,
        attribute_name: models.BigIntegerField(verbose_name=f"{attribute_name} in cents (¢)"),
        dollar_propery_name: property(get_amount),
    }
    base_classes = (models.Model,)

    return type(class_name, base_classes, attrs)


Amountable = create_price_class("Amountable", "amount")
Priceable = create_price_class("Priceable", "price")
Discountable = create_price_class("Discountable", "discount")
Valuable = create_price_class("Valuable", "value")
