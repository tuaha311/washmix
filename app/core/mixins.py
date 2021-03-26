from django.db.models import ManyToManyField

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

        # if object doesn't have a `.pk` Primary Key
        # it means, that object created right now and we can't emit signal.
        if not obj.pk:
            obj.save()

        update_fields = set(form.changed_data)
        model_fields = obj._meta.get_fields()

        model_fields_without_m2m = [
            item for item in model_fields if not isinstance(item, ManyToManyField)
        ]
        model_unique_fields = set([item.name for item in model_fields_without_m2m])
        model_updated_fields = update_fields & model_unique_fields

        obj.save(update_fields=model_updated_fields)
