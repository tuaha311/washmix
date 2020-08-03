from django.db import models

from core.common_models import Common


class Notification(Common):
    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        related_name="notification_list",
        on_delete=models.CASCADE,
    )

    message = models.TextField(
        verbose_name="message",
    )

    class Meta:
        verbose_name = "notification"
        verbose_name_plural = "notifications"
