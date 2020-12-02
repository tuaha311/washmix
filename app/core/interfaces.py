from abc import ABC, abstractmethod


class PaymentInterfaceService(ABC):
    @abstractmethod
    def charge(self, **kwargs):
        pass

    @abstractmethod
    def create_invoice(self, **kwargs):
        pass
