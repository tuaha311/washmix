from users.models import Client


class CheckoutHelper:
    def __init__(self, client: Client):
        self._client = client

    def checkout(self):
        pass
