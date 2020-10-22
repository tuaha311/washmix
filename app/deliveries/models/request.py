from django.db import models

from core.common_models import Common
from deliveries.choices import Kind, Status
from deliveries.common_models import CommonDeliveries


class Request(CommonDeliveries, Common):
    """
    Client-side entity.
    """

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        on_delete=models.CASCADE,
        related_name="request_list",
    )
    pickup = models.OneToOneField(
        "deliveries.Delivery",
        verbose_name="pickup delivery",
        related_name="+",
        on_delete=models.PROTECT,
    )
    dropoff = models.OneToOneField(
        "deliveries.Delivery",
        verbose_name="dropoff delivery",
        related_name="+",
        on_delete=models.PROTECT,
    )
    schedule = models.ForeignKey(
        "deliveries.Schedule",
        verbose_name="recurring schedule of delivery",
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


