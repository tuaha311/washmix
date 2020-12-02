from abc import ABC, abstractmethod
from typing import Any

from core.utils import get_dollars


class BaseAmountContainer(ABC):
    """
    Container that adds properties of money.
    By default, proxies all not found attributes to proxy object (model instance)
    defined via `proxy_to_object` attribute.

    Attributes are read-write - if you write to them, they will be proxied to model instance
    if attribute not defined as private (not starts with '_').
    """

    proxy_to_object = ""

    @property
    @abstractmethod
    def amount(self) -> int:
        pass

    @property
    @abstractmethod
    def discount(self) -> float:
        pass

    @property
    def dollar_amount(self) -> float:
        return get_dollars(self, "amount")

    @property
    def proxy(self):
        proxy_key = self.proxy_to_object
        return getattr(self, proxy_key)

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

    def __getattr__(self, item: str):
        """
        This method invoked only when we can't find attribute name in itself.
        Method works as a fallback.
        """

        # we are preventing recursive call of getattr
        if item == "proxy":
            return self.proxy

        proxy_object = self.proxy
        return getattr(proxy_object, item)

    def __setattr__(self, key: str, value: Any):
        """
        Method allows to set attributes on proxy object (model instance) if
        attribute defined as public (i.e. not starts with '_').
        """

        super().__setattr__(key, value)

        if key.startswith("_"):
            return None

        proxy_object = self.proxy
        setattr(proxy_object, key, value)
