from django.conf import settings
from django.db import models

from core.common_models import Common


class Card(Common):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="card_list"
    )
    stripe_card_id = models.TextField()
    is_active = models.BooleanField(default=False)
