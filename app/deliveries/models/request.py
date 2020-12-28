from django.db import models

from core.common_models import Common
from deliveries.choices import Kind
from deliveries.common_models import CommonScheduleRequest


class Request(CommonScheduleRequest, Common):
    """
    Client-side entity.

    Request for pickup and dropoff from our Client.
    It can be made via dashboard or via SMS to Twilio Flex.

    When we receive date for pickup delivery date and interval, we are calculating
    dropoff date and dropoff interval based on our business rules.

    At incoming Request we are creating 2 Delivery records - one for pickup,
    one for dropoff.

    With proxy @property fields we are hiding `pickup` and `dropoff` from frontend -
    we are changing them like usual properties for frontend. In reality they are
    a separate objects (Delivery) and we show them in Drivers feed.

    NOTE: Request / Schedule uses the same pattern such Package / Subscription.
    NOTE: Be careful with proxy @property - save a ref to object before changing.
    Example without ref:
    > self.pickup.date = datetime(2020, 10, 20)
    > self.pickup.save()
    > self.pickup.date
    > datetime(2020, 10, 10)

    Doesn't work because every time when we call `self.pickup` it returns another object:
    > id(self.pickup) == id(self.pickup)
    > False

    Alternative:
    > pickup = self.pickup
    > pickup.date = datetime(2020, 10, 20)
    > pickup.save()
    Works because we saved a ref to original object.
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
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "request"
        verbose_name_plural = "requests"

    def __str__(self):
        return f"# {self.id}"

    @property
    def pretty_pickup_message(self) -> str:
        pretty_date = self.pickup.pretty_date

        return pretty_date

    #
    # pickup proxy fields
    #
    @property
    def pickup(self):
        return self.delivery_list.get(kind=Kind.PICKUP)

    @property
    def pickup_date(self):
        return self.pickup.date

    @pickup_date.setter
    def pickup_date(self, value):
        pickup = self.pickup
        pickup.date = value
        pickup.save()

    @property
    def pickup_start(self):
        return self.pickup.start

    @pickup_start.setter
    def pickup_start(self, value):
        pickup = self.pickup
        pickup.start = value
        pickup.save()

    @property
    def pickup_end(self):
        return self.pickup.end

    @pickup_end.setter
    def pickup_end(self, value):
        pickup = self.pickup
        pickup.end = value
        pickup.save()

    @property
    def pickup_invoice(self):
        return self.pickup.invoice

    @pickup_invoice.setter
    def pickup_invoice(self, value):
        pickup = self.pickup
        pickup.invoice = value
        pickup.save()

    @property
    def pickup_status(self):
        return self.pickup.get_status_display()

    #
    # dropoff proxy fields
    #
    @property
    def dropoff(self):
        return self.delivery_list.get(kind=Kind.DROPOFF)

    @property
    def dropoff_date(self):
        return self.dropoff.date

    @dropoff_date.setter
    def dropoff_date(self, value):
        dropoff = self.dropoff
        dropoff.date = value
        dropoff.save()

    @property
    def dropoff_start(self):
        return self.dropoff.start

    @dropoff_start.setter
    def dropoff_start(self, value):
        dropoff = self.dropoff
        dropoff.start = value
        dropoff.save()

    @property
    def dropoff_end(self):
        return self.dropoff.end

    @dropoff_end.setter
    def dropoff_end(self, value):
        dropoff = self.dropoff
        dropoff.end = value
        dropoff.save()

    @property
    def dropoff_invoice(self):
        return self.dropoff.invoice

    @dropoff_invoice.setter
    def dropoff_invoice(self, value):
        dropoff = self.dropoff
        dropoff.invoice = value
        dropoff.save()

    @property
    def dropoff_status(self):
        return self.dropoff.get_status_display()

