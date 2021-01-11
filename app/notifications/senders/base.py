from abc import ABC, abstractmethod


class Sender(ABC):
    @abstractmethod
    def send(self, recipient_list: list, event: str, context: dict = None, *args, **kwargs):
        pass

    @abstractmethod
    def raw_send(
        self,
        from_sender: str,
        recipient_list: list,
        subject: str,
        body: str,
        *args,
        **kwargs,
    ):
        pass
