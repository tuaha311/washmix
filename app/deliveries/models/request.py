from django.db import models

from core.common_models import Common
from deliveries.choices import Kind
from deliveries.common_models import CommonScheduleRequest


class Request(CommonScheduleRequest, Common):
    """
    Client-side entity.

    NOTE: Request / Schedule uses the same pattern such Package / Subscription.

    Request for pickup and dropoff from our Client.
    It can be made via dashboard or via SMS to Twilio Flex.

    When we receive date for pickup delivery date and interval, we are calculating
    dropoff date and dropoff interval based on our business rules.

    At incoming Request we are creating 2 Delivery records - one for pickup,
    one for dropoff.
    """

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        on_delete=models.CASCADE,
        related_name="request_list",
    )
    address = models.ForeignKey(
        "locations.Address",
        verbose_name="address to pickup and dropoff",
        related_name="request_list",
        on_delete=models.CASCADE,
    )
    schedule = models.ForeignKey(
        "deliveries.Schedule",
        verbose_name="recurring schedule for request",
        related_name="request_list",
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = "request"
        verbose_name_plural = "requests"

    #
    # pickup proxy fields
    #
    @property
    def pickup(self):
        return self.delivery_list.get(kind=Kind.PICKUP)

    @pickup.setter
    def pickup(self, value):
        self.pickup = value
        self.save()

    @property
    def pickup_date(self):
        return self.pickup.date

    @pickup_date.setter
    def pickup_date(self, value):
        self.pickup.date = value
        self.pickup.save()

    @property
    def pickup_start(self):
        return self.pickup.start

    @pickup_start.setter
    def pickup_start(self, value):
        self.pickup.start = value
        self.pickup.save()

    @property
    def pickup_end(self):
        return self.pickup.end

    @pickup_end.setter
    def pickup_end(self, value):
        self.pickup.end = value
        self.pickup.save()

    #
    # dropoff proxy fields
    #
    @property
    def dropoff(self):
        return self.delivery_list.get(kind=Kind.DROPOFF)

    @dropoff.setter
    def dropoff(self, value):
        self.dropoff = value
        self.save()

    @property
    def dropoff_date(self):
        return self.dropoff.date

    @dropoff_date.setter
    def dropoff_date(self, value):
        self.dropoff.date = value
        self.dropoff.save()

    @property
    def dropoff_start(self):
        return self.dropoff.start

    @dropoff_start.setter
    def dropoff_start(self, value):
        self.dropoff.start = value
        self.dropoff.save()

    @property
    def dropoff_end(self):
        return self.dropoff.end

    @dropoff_end.setter
    def dropoff_end(self, value):
        self.dropoff.end = value
        self.dropoff.save()


