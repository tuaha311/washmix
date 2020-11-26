from django.conf import settings
from django.db import models
from django.utils.timezone import localdate, localtime, now

from core.common_models import Common
from users.choices import EmployeePosition


class Employee(Common):
    """
    Service-side entity.

    Employee of laundry who processing orders or who delivers
    orders to clients.

    At the moment of 31/07/2020 we can divide them into 3 main categories:
    - Laundress (who cares about clean, wash, fold etc.)
    - Driver (who responsible of delivery and pickup)
    - Manager (who manages laundress and drivers)

    Laundress and Manager can login into WashMix Admin and use it for
    order management.
    Driver mostly uses a WashMix Driver's App to deliver and pickup orders.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee",
    )

    position = models.CharField(
        verbose_name="position of employee",
        max_length=20,
        choices=EmployeePosition.CHOICES,
        default=EmployeePosition.LAUNDRESS,
    )
    SSN = models.CharField(
        verbose_name="social security number",
        max_length=15,
        null=True,
    )
    birthday = models.DateField(
        verbose_name="date of birthday",
        default=localdate,
        null=True,
    )
    came_to_work = models.DateTimeField(
        verbose_name="came out to work from",
        default=now,
        null=True,
    )

    class Meta:
        verbose_name = "employee"
        verbose_name_plural = "employees"
