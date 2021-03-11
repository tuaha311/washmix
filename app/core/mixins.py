from core.utils import get_dollars


class CalculatedAmountWithDiscountMixin:
    """
    Mixin that used to add properties to models with billing:
        - amount_with_discount
        - dollar_amount_with_discount

    """

    amount: int
    discount: int

    @property
    def amount_with_discount(self) -> int:
        amount = self.amount
        discount = self.discount

        return amount - discount

    @property
    def dollar_amount_with_discount(self) -> float:
        return get_dollars(self, "amount_with_discount")


class CalculatedDiscountMixin:
    """
    Mixin that adds a property to transform discount into dollars:
        - dollar_discount
    """

    @property
    def dollar_discount(self) -> float:
        return get_dollars(self, "discount")


class AdminUpdateFieldsMixin:
    """
    Mixin for Admin Panel that re-implement `save_model` method
    to fire signals - we will proxy `update_fields` into `Model.save()` method.

    More info about signal - https://docs.djangoproject.com/en/3.1/ref/signals/#post-save

    Method original location - django.contrib.admin.options.ModelAdmin#save_model
    """

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """

        update_fields = set(form.changed_data)

        obj.save(update_fields=update_fields)
