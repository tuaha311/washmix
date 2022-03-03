from django.db import models

from core.common_models import Common


class NotificationTypes:
    NEW_ORDER = "new_order"
    NEW_SIGNUP = "new_signup"
    NEW_PICKUP_REQUEST = "new_pickup_request"
    PICKUP_DATE_CHANGE = "pickup_date_change"
    PICKUP_REQUEST_CANCELED = "pickup_request_canceled"
    DROPOFF_DUE_TODAY = "dropoff_due_today"
    POTENTIAL_CUSTOMER = "potential_customer"

    MAP = {
        NEW_ORDER: "created new order",
        NEW_SIGNUP: "signed up",
        NEW_PICKUP_REQUEST: "created new pickup request",
        PICKUP_DATE_CHANGE: "changed the pickup date",
        PICKUP_REQUEST_CANCELED: "canceled the pickup request",
        DROPOFF_DUE_TODAY: "drop-off is due today",
        POTENTIAL_CUSTOMER: "added to potential customer",
    }
    CHOICES = list(MAP.items())

class Notification(Common):
    """
    Admin side Entity
    Saves all the notifications accessible form Admin panel
    """

    message = models.CharField(
        verbose_name="notification type",
        choices=NotificationTypes.CHOICES,
        max_length=80,
    )

    description = models.CharField(
        verbose_name="short description",
        choices=NotificationTypes.CHOICES,
        max_length=100,
        null=True
    )

    user_triggered = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    customer_triggered = models.ForeignKey(
        "users.Customer",
        verbose_name="customer",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    is_read = models.BooleanField(
        verbose_name="message read",
        default=False
    )

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    # def __str__(self):
    #     return f"{self.user_triggered.full_name()} {self.message}"

    def notification_read(self):
        self.is_read = True
        self.save()

    @staticmethod
    def create_notification(client, message, customer_triggered=None, **kwargs):
        Notification.objects.create(user_triggered=client, message=message, customer_triggered=customer_triggered, **kwargs)
