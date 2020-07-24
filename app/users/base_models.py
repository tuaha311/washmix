from django.conf import settings
from django.db import models
from django.utils.timezone import localdate

from core.common_models import Common


class AbstractEmployee(Common):
    """
    Abstract class that implements most of field
    required by employees.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee",
    )

    SSN = models.CharField(
        verbose_name="social security number",
        max_length=15,
        null=True,
    )
    birthday = models.DateField(
        verbose_name="date of birthday",
        null=True,
    )
    came_to_work = models.DateTimeField(
        verbose_name="came out to work from",
        default=localdate,
        null=True,
    )

    class Meta:
        abstract = True
