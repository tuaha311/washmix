from users.models import Client


class ExtrasService:
    def __init__(self, client: Client):
        self._client = client

    @property
    def extras(self):
        pass
