from django.db import models
from django.utils.timezone import localtime

from core.common_models import Common
from modules.enums import CouponType


class Invoice(Common):
    """
    """


    def __str__(self):
        return self.code
