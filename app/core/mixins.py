from core.utils import get_dollars


class CalculatedAmountWithDiscount:
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
    @property
    def dollar_discount(self) -> float:
        return get_dollars(self, "discount")
