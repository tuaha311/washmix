import arrow
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import redis
from rest_framework_expiring_authtoken.models import ExpiringToken

from modules.constant import AppUsers, CouponType, Crease, Detergents, SignUp, Starch
from utilities.wm_message_config import order_dropoff, order_pickup


class PickupAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pickupaddress")
    address_line_1 = models.TextField()
    address_line_2 = models.TextField(default="")
    state = models.CharField(max_length=30, default="")
    city = models.CharField(max_length=30)
    zip_code = models.CharField(max_length=30)
    title = models.CharField(max_length=80, default="")

    added_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)


class DropoffAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dropoffaddress")
    address_line_1 = models.TextField()
    address_line_2 = models.TextField(default="")
    state = models.CharField(max_length=30, default="")
    city = models.CharField(max_length=30)
    zip_code = models.CharField(max_length=30)
    title = models.CharField(max_length=80, default="")

    added_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="order")

    pickup_address = models.ForeignKey(PickupAddress, default=None, on_delete=models.CASCADE)
    dropoff_address = models.ForeignKey(DropoffAddress, default=None, on_delete=models.CASCADE)
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

        # Check if we have scheduled a notification for this order before
        if self.task_id_pickup and self.task_id_dropoff:
            # Revoke that task in case its time has changed
            self.cancel_task(self.task_id_pickup)
            self.cancel_task(self.task_id_dropoff)
            # celery_app.control.revoke(self.task_id_pickup)
            # celery_app.control.revoke(self.task_id_dropoff)

        # Save order, which populates self.pk,
        # which is used in schedule_notification
        super(Order, self).save()

        # Schedule a new notification task for this order
        self.task_id_pickup = self.schedule_notification(
            order_pickup(user=self.user, order=self), self.pick_up_from_datetime
        )
        self.task_id_dropoff = self.schedule_notification(
            order_dropoff(user=self.user, order=self), self.drop_off_from_datetime
        )

        # Save order again, with the new task_ids
        super(Order, self).save()


class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    item = models.TextField(default="")
    cost = models.FloatField(default=0)


class UserMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(default="")
    added_datetime = models.DateTimeField(auto_now_add=True)


class AddressOrder(models.Model):
    address = models.ForeignKey(PickupAddress, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)


class PackageType(models.Model):
    package_name = models.TextField(default="")
    package_price = models.FloatField(default=0)


class Profile(models.Model):
    """User profile to save extra info other than related to authentication."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    package_id = models.ForeignKey(PackageType, null=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, default="")

    # Additional employee information
    DOB = models.DateField(null=True)
    joining_date = models.DateField(null=True)
    SSN = models.CharField(max_length=15, null=True)

    # Customer information
    is_doormen = models.BooleanField(default=False)

    stripe_customer_id = models.TextField(null=True)
    balance = models.FloatField(default=0)
    # Preferences
    detergents = models.CharField(
        max_length=50, choices=[(item, item.value) for item in Detergents], null=True
    )
    starch = models.CharField(
        max_length=50, choices=[(item, item.value) for item in Starch], null=True
    )
    no_crease = models.CharField(
        max_length=50, choices=[(item, item.value) for item in Crease], null=True
    )
    app_users = models.CharField(
        max_length=30,
        choices=[(item, item.value) for item in AppUsers],
        null=True,
        default=AppUsers.REGULAR_USERS.value,
    )
    authentication_provider = models.CharField(
        max_length=30,
        choices=[(item, item.value) for item in SignUp],
        null=True,
        default=SignUp.washmix.value,
    )

    fabric_softener = models.BooleanField(default=False)
    fix_tears = models.BooleanField(default=False)
    is_coupon = models.BooleanField(default=False)


class CustomToken(models.Model):
    """Custom model token, for adding up extended life token info"""

    expiring_token = models.OneToOneField(ExpiringToken, on_delete=models.CASCADE)
    is_long_lived = models.BooleanField(default=True)


class UserCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_card")
    stripe_card_id = models.TextField()
    is_active = models.BooleanField(default=False)
    added_datetime = models.DateTimeField(auto_now_add=True)


class Coupons(models.Model):
    name = models.CharField(max_length=30)
    amount_off = models.FloatField(default=0)
    percentage_off = models.FloatField(default=0)
    start_date = models.DateTimeField(default=timezone.now())
    valid = models.BooleanField(default=True)
    max_redemptions = models.IntegerField(default=1)
    coupon_type = models.CharField(
        max_length=30,
        choices=[(item, item.value) for item in CouponType],
        null=True,
        default=CouponType.FIRST.value,
    )

    added_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    def apply_coupon(self, total_amount):
        return (self.percentage_off * total_amount) / 100


class Product(models.Model):
    name = models.CharField(max_length=50)
    product = models.ForeignKey(
        "self", null=True, related_name="children", on_delete=models.CASCADE
    )
    price = models.FloatField(default=0)


# class Balance(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     current_balance = models.FloatField(null=False)
#     added_datetime = models.DateTimeField(auto_now_add=True)
#     updated_datetime = models.DateTimeField(auto_now=True)
#
# class UserPurchases(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     type = models.CharField(max_length=100, null=False)
#     value = models.CharField(max_length=100, null=False)
#     cost = models.FloatField(null=False)
#     added_datetime = models.DateTimeField(auto_now_add=True)
#     updated_datetime = models.DateTimeField(auto_now=True)
