from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from core.common_models import Common
from pickups.common_models import CommonScheduleDelivery


class Schedule(CommonScheduleDelivery, Common):
    """
    NOTE: Schedule / Delivery uses the same pattern such Package / Subscription.

    It is templates of scheduled deliveries.
    We are using this to create concrete instances of Schedule called Delivery.

    You can change schedule to another weekdays or pause it.
    """

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        related_name="schedule_list",
        on_delete=models.CASCADE,
    )
    days = ArrayField(
        base_field=models.PositiveSmallIntegerField(
            verbose_name="day of week",
            choices=settings.DELIVERY_DAY_CHOICES,
        ),
        verbose_name="recurring pickup days",
        max_length=7,
    )
    status = models.CharField(
        max_length=20,
        verbose_name="status of schedule",
        choices=settings.DELIVERY_STATUS_CHOICES,
    )

    class Meta:
        verbose_name = "schedule"
        verbose_name_plural = "schedules"
