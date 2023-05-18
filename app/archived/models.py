from django.db import models

from core.common_models import Common
from core.validators import validate_phone
from deliveries.models import Delivery, Request
from users.choices import CustomerKind


class ArchivedRequest(Request):
    class Meta:
        proxy = True
        verbose_name = "Request"
        verbose_name_plural = "Requests"
        ordering = ["-created"]


class ArchivedDelivery(Delivery):
    class Meta:
        proxy = True
        verbose_name = "Delivery"
        verbose_name_plural = "Deliveries"
        ordering = ["-date", "sorting", ]


class ArchivedCustomer(Common):
    """
    Users who could'nt signup completely and were achived
    to give them clean slate after 3 hours
    """

    email = models.EmailField(
        verbose_name="email",
        null=True,
        blank=True
    )
    phone = models.CharField(
        verbose_name="phone",
        max_length=20,
        null=True,
        blank=True,
        validators=[validate_phone],
    )
    full_name = models.CharField(
        verbose_name="full name",
        max_length=100,
        blank=True,
    )
    zip_code = models.CharField(
        verbose_name="zip code",
        max_length=20,
        blank=True,
    )
    address = models.CharField(
        verbose_name="address",
        max_length=250,
        blank=True,
    )
    kind = models.CharField(
        verbose_name="kind",
        max_length=20,
        default=CustomerKind.INTERESTED,
        choices=CustomerKind.CHOICES,
    )

    promo_emails_sent_count = models.PositiveSmallIntegerField(
        verbose_name="promo emails sent count",
        default=0,
        blank=True,
        editable=False,
    )

    next_promo_email_schedule = models.DateTimeField(
        verbose_name="next promo email schedule",
        editable=False,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Archived Customer"
        verbose_name_plural = "Archived Customers"

    def __str__(self):
        return f"#{self.id}"

    def set_next_promo_email_schedule(self, time_delta_to_add):
        next_schedule_time = self.next_promo_email_schedule + time_delta_to_add
        self.next_promo_email_schedule = next_schedule_time

    def increase_promo_emails_sent_count(self):
        self.promo_emails_sent_count += 1