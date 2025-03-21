from django.db import models
from django.utils.functional import cached_property

from core.common_models import CommonAmountDiscountModel
from deliveries.choices import DeliveryKind
from deliveries.common_models import CommonScheduleRequest


class Request(CommonScheduleRequest, CommonAmountDiscountModel):
    """
    Client-side entity.

    Request has multiple orders and order has single request.
    Request has multiple deliveries and delivery has single request.

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

    rush_amount = models.BigIntegerField(
        verbose_name="rush delivery price, in cents (¢)",
        default=0,
    )
    is_custom = models.BooleanField(
        verbose_name="is a custom delivery price",
        default=False,
    )
    custom_amount = models.BigIntegerField(
        verbose_name="custom delivery price, in cents (¢)",
        default=0,
    )

    unpaid_reminder_email_count = models.PositiveSmallIntegerField(
        verbose_name="Unpaid Order Reminder Email",
        default=0,
        blank=True,
        editable=False,
    )

    unpaid_reminder_email_time = models.DateTimeField(
        verbose_name="Reminder Email Time",
        editable=False,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "request"
        verbose_name_plural = "requests"
        ordering = ["-created"]

    def __str__(self):
        return f"# {self.id}"

    @property
    def pretty_pickup_message(self) -> str:
        pretty_date = self.pickup.pretty_date

        return pretty_date

    #
    # pickup proxy fields
    #
    @cached_property
    def pickup(self):
        return self.delivery_list.get(kind=DeliveryKind.PICKUP)

    @property
    def pickup_date(self):
        return self.pickup.date

    @pickup_date.setter
    def pickup_date(self, value):
        pickup = self.pickup
        pickup.date = value

        # defining which fields was changed - used in Delivery signal
        pickup.save(update_fields={"date"})

    @property
    def pickup_start(self):
        return self.pickup.start

    @pickup_start.setter
    def pickup_start(self, value):
        pickup = self.pickup
        pickup.start = value

        # defining which fields was changed - used in Delivery signal
        pickup.save(update_fields={"start"})

    @property
    def pickup_end(self):
        return self.pickup.end

    @pickup_end.setter
    def pickup_end(self, value):
        pickup = self.pickup
        pickup.end = value

        # defining which fields was changed - used in Delivery signal
        pickup.save(update_fields={"end"})

    @property
    def pickup_status(self):
        return self.pickup.get_status_display()

    #
    # dropoff proxy fields
    #
    @cached_property
    def dropoff(self):
        return self.delivery_list.get(kind=DeliveryKind.DROPOFF)

    @property
    def dropoff_date(self):
        return self.dropoff.date

    @dropoff_date.setter
    def dropoff_date(self, value):
        dropoff = self.dropoff
        dropoff.date = value

        # defining which fields was changed - used in Delivery signal
        dropoff.save(update_fields={"date"})

    @property
    def dropoff_start(self):
        return self.dropoff.start

    @dropoff_start.setter
    def dropoff_start(self, value):
        dropoff = self.dropoff
        dropoff.start = value

        # defining which fields was changed - used in Delivery signal
        dropoff.save(update_fields={"start"})

    @property
    def dropoff_end(self):
        return self.dropoff.end

    @dropoff_end.setter
    def dropoff_end(self, value):
        dropoff = self.dropoff
        dropoff.end = value

        # defining which fields was changed - used in Delivery signal
        dropoff.save(update_fields={"end"})

    @property
    def dropoff_status(self):
        return self.dropoff.get_status_display()

    def increase_unpaid_reminder_email_count(self):
        self.unpaid_reminder_email_count =self.unpaid_reminder_email_count + 1

    def set_unpaid_order_reminder_email_time(self, time_to_send):
        self.unpaid_reminder_email_time = time_to_send

    @property
    def unpaid_order_reminder_email_time(self):
        return self.unpaid_reminder_email_time

    @property
    def unpaid_order_reminder_count(self):
        return self.unpaid_reminder_email_count