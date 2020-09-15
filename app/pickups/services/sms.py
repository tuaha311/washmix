from datetime import datetime

from django.conf import settings

from core.models import Phone
from users.models.customer import Customer


class TwilioFlexService:
    def __init__(self, message: str, contact: str, date_n_time: datetime) -> None:
        self._message = message
        self._contact = contact
        self._date_n_time = date_n_time

    def handle(self):
        try:
            # we can check only Phone table, because inside it
            # we have a full list of valid client phones.
            # if phone number doesn't exists inside Phone table -
            # it means, that Client hasn't using our web application and
            # admin should handle this case manually.
            Phone.objects.get(number=self._contact)

            return settings.SUCCESS

        except Phone.DoesNotExist:
            Customer.objects.get_or_create(
                phone=self._contact, defaults={"kind": Customer.POSSIBLE,}
            )

            return settings.FAIL
