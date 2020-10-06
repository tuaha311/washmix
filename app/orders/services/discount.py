from users.models import Client


class DiscountService:
    def __init__(self, client: Client):
        self._client = client

    @property
    def discounts(self):
        pass
