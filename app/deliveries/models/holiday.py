from django.db import models

from core.common_models import Common


class Holiday(Common):
    date = models.DateField(
        verbose_name="date"
    )
