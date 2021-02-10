from abc import ABC, abstractmethod
from typing import List, Optional

from billing.models import Invoice
from deliveries.models import Request
from orders.models import Basket, Order
from subscriptions.models import Subscription


class PaymentInterfaceService(ABC):
    @abstractmethod
    def confirm(
        self,
        request: Optional[Request],
        basket: Optional[Basket],
        subscription: Optional[Subscription],
        invoice: Invoice,
        **kwargs,
    ):
        pass

    @abstractmethod
    def refresh_amount_with_discount(
        self,
        order: Order,
        basket: Optional[Basket],
        request: Optional[Request],
        subscription: Optional[Subscription],
        **kwargs,
    ) -> Optional[float]:
        pass

    @abstractmethod
    def checkout(self, order: Order, subscription: Subscription, **kwargs):
        pass
