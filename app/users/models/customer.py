from django.db import models

from core.common_models import Common
from core.validators import validate_phone


class Customer(Common):
    """
    OFFLINE-ONLY customer. They can't login or use our web application.
    We gather information about them to use in future.

    At the moment of 31/07/2020 we can divide 2 main groups of offline users:
    - Interested (came from landing page, waiting for our start in their city)
    - Possible (current customers, who can't use a smartphone to browse the Web
    and can only send SMS to make orders)
    """

    INTERESTED = "interested"
    POSSIBLE = "possible"
    KIND_MAP = {
        INTERESTED: "Who interested in our services in future",
        POSSIBLE: ("Who uses only SMS orders and "
                   "maybe will use web-application in future")
    }
    KIND_CHOICES = list(KIND_MAP.items())

    email = models.EmailField(
        verbose_name="email",
        unique=True,
        null=True,
    )
    phone = models.CharField(
        verbose_name="phone",
        max_length=20,
        unique=True,
        null=True,
        validators=[validate_phone],
    )
    zip_code = models.CharField(
        verbose_name="zip code",
        max_length=20,
        blank=True,
    )
    kind = models.CharField(
        verbose_name="kind",
        max_length=20,
        choices=KIND_CHOICES,
    )

    class Meta:
        verbose_name = "customer"
        verbose_name_plural = "customers"
