from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from rest_framework_expiring_authtoken.models import ExpiringToken

from modules.enums import AppUsers, Crease, Detergents, SignUp, Starch
from core.common_models import Common


class Profile(Common):
    """User profile to save extra info other than related to authentication."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    package_id = models.ForeignKey("core.PackageType", null=True, on_delete=models.CASCADE)
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


class CustomToken(Common):
    """Custom model token, for adding up extended life token info"""

    expiring_token = models.OneToOneField(ExpiringToken, on_delete=models.CASCADE)
    is_long_lived = models.BooleanField(default=True)


class UserCard(Common):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_card"
    )
    stripe_card_id = models.TextField()
    is_active = models.BooleanField(default=False)
    added_datetime = models.DateTimeField(auto_now_add=True)


class UserMessage(Common):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(default="")
    added_datetime = models.DateTimeField(auto_now_add=True)
