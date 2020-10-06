from users.models import Client


class DeliveryService:
    def __init__(self, client: Client):
        self._client = client

    @property
    def delivery(self):
        pass
