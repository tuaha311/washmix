from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

import arrow
import redis

from core.common_models import Common


class Order(Common):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="order")

    pickup_address = models.ForeignKey("core.PickupAddress", default=None, on_delete=models.CASCADE)
    dropoff_address = models.ForeignKey(
        "core.DropoffAddress", default=None, on_delete=models.CASCADE
    )
    next_day_delivery = models.BooleanField(default=False)
    same_day_delivery = models.BooleanField(default=False)

    pick_up_from_datetime = models.DateTimeField(default=timezone.now)
    pick_up_to_datetime = models.DateTimeField(default=timezone.now)

    drop_off_from_datetime = models.DateTimeField(default=timezone.now)
    drop_off_to_datetime = models.DateTimeField(default=timezone.now)

    instructions = models.TextField(blank=True)
    additional_notes = models.TextField(blank=True)

    added_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    total_cost = models.FloatField(default=0.0)

    discount_description = models.TextField(blank=True)
    discount_amount = models.FloatField(default=0)

    count = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=False)

    # Additional fields not visible to users
    task_id_pickup = models.CharField(max_length=50, blank=True, editable=False)
    task_id_dropoff = models.CharField(max_length=50, blank=True, editable=False)

    def schedule_notification(self, message_formatter, reminder_time):
        """Schedules a task to send a notification about this order"""

        # Schedule the task
        from tasks import send_sms_reminder

        reminder_time = arrow.get(reminder_time)
        reminder_time = reminder_time.shift(minutes=-5)

        now = arrow.now(timezone.get_current_timezone_name())
        reminder_time = int((reminder_time - now).total_seconds()) * 1000
        result = send_sms_reminder.send_with_options(
            args=(self.pk, message_formatter(), settings.TEAM_WASHMIX,), delay=reminder_time,
        )

        return result.options["redis_message_id"]

    def cancel_task(self, task_id):
        redis_client = redis.Redis(host="localhost", port=6379, db=0)
        redis_client.hdel("dramatiq:default.DQ.msgs", task_id)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Overiding models save method to avoid sending duplication sms notification for same order.
           It checks if sms notification is already schedule for the order using 'task_ids'."""

        from utilities.email_formatters import format_order_dropoff, format_order_pickup

        # Check if we have scheduled a notification for this order before
        if self.task_id_pickup and self.task_id_dropoff:
            # Revoke that task in case its time has changed
            self.cancel_task(self.task_id_pickup)
            self.cancel_task(self.task_id_dropoff)

        # Save order, which populates self.pk,
        # which is used in schedule_notification
        super(Order, self).save()

        # Schedule a new notification task for this order
        self.task_id_pickup = self.schedule_notification(
            format_order_pickup(user=self.user, order=self), self.pick_up_from_datetime
        )
        self.task_id_dropoff = self.schedule_notification(
            format_order_dropoff(user=self.user, order=self), self.drop_off_from_datetime
        )

        # Save order again, with the new task_ids
        super(Order, self).save()


class OrderItems(Common):
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="order_items")
    item = models.TextField(default="")
    cost = models.FloatField(default=0)


class AddressOrder(Common):
    address = models.ForeignKey("core.PickupAddress", on_delete=models.CASCADE)
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE)
