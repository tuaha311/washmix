from django.db import models
from locations.models import ZipCode

from core.common_models import Common
from deliveries.choices import WeekDays


class CategorizeRoute(Common):
    day = models.CharField(
        max_length=2,
        verbose_name="Day",
        choices=WeekDays.CHOICES,
        unique=True,
    )
    zip_codes = models.ManyToManyField(
        ZipCode,
        verbose_name="Zip Codes",
    )

    class Meta:
        verbose_name_plural = "Categorized Routes"
    