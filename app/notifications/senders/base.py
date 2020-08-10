from abc import ABC, abstractmethod


class Sender(ABC):
    @abstractmethod
    def send(self, *args, **kwargs):
        pass

    @abstractmethod
    def raw_send(self, *args, **kwargs):
        pass
