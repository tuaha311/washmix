from datetime import datetime

from django.conf import settings

from core.models import Phone
from users.models.customer import Customer


class FlexService:
    def __init__(self, message: str, contact: str, date_n_time: datetime) -> None:
        self._message = message
        self._contact = contact
        self._date_n_time = date_n_time

    def handle(self):
        try:
            # we are trying to find a Client with a phone number
            Phone.objects.get(number=self._contact)

            return settings.SUCCESS

        except Phone.DoesNotExist:
            Customer.objects.get_or_create(
                phobe=self._contact, defaults={"kind": Customer.POSSIBLE,}
            )

            return settings.FAIL
