from django.db import models

from core.common_models import Common
from core.validators import validate_phone
from users.choices import CustomerKind


class Log(Common):
    """
    Admin Logs
    All customer related Logs
    """

    action = models.CharField(max_length=255)
    customer = models.CharField(max_length=255)
