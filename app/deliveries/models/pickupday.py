from django.db import models

from core.common_models import Common
from deliveries.choices import PickupDays


class PickupDay(Common):
    day = models.CharField(
        max_length=20,
        verbose_name="day",
        choices=PickupDays.CHOICES,
        null=True,
        blank=True
    )