from django.contrib import admin

from billing.models import Coupon, Invoice, Transaction
from core.admin import DefaultAdmin

models = [[Transaction], [Coupon, DefaultAdmin], [Invoice, DefaultAdmin]]
for item in models:
    admin.site.register(*item)
