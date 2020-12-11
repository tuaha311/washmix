from django.contrib import admin

from billing.models import Coupon, Transaction
from core.admin import DefaultAdmin

models = [[Transaction], [Coupon, DefaultAdmin]]
for item in models:
    admin.site.register(*item)
