from abc import ABC, abstractmethod
from typing import List, Optional

from billing.models import Invoice
from deliveries.models import Request
from orders.models import Basket, Order
from subscriptions.models import Subscription


class PaymentInterfaceService(ABC):
    @abstractmethod
    def charge(
        self,
        request: Optional[Request],
        basket: Optional[Basket],
        subscription: Optional[Subscription],
        **kwargs,
    ):
        pass

    @abstractmethod
    def create_invoice(
        self,
        order: Order,
        basket: Optional[Basket],
        request: Optional[Request],
        subscription: Optional[Subscription],
        **kwargs,
    ) -> Optional[List[Invoice]]:
        pass

    @abstractmethod
    def checkout(self, order: Order, subscription: Subscription, **kwargs):
        pass
