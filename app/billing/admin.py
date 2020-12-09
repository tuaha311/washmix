from django.contrib import admin

from billing.models import Card, Coupon, Invoice, Transaction
from core.admin import DefaultAdmin

models = [[Card], [Transaction], [Coupon, DefaultAdmin], [Invoice, DefaultAdmin]]
for item in models:
    admin.site.register(*item)
