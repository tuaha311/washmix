from abc import abstractmethod

from core.utils import get_dollars


class BaseAmountContainer:
    proxy_to_object = ""

    @property
    @abstractmethod
    def amount(self) -> int:
        pass

    @property
    def dollar_amount(self) -> float:
        return get_dollars(self, "amount")

    @property
    @abstractmethod
    def discount(self) -> float:
        pass

    @property
    def dollar_discount(self) -> float:
        return get_dollars(self, "discount")

    @property
    def amount_with_discount(self) -> float:
        amount = self.amount
        discount = self.discount

        return amount - discount

    @property
    def dollar_amount_with_discount(self) -> float:
        return get_dollars(self, "amount_with_discount")

    def __getattr__(self, item):
        """
        This method invoked only when we can't find attribute name in itself.
        Method works as a fallback.
        """

        proxy_object = getattr(self, self.proxy_to_object)
        return getattr(proxy_object, item)
