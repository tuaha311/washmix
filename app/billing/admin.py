from django.contrib import admin

from billing.models import Coupon, Invoice, Transaction
from core.admin import AdminWithSearch


class TransactionAdmin(admin.ModelAdmin):
    readonly_fields = [
        "stripe_id",
    ]


models = [[Transaction, TransactionAdmin], [Coupon, AdminWithSearch], [Invoice, AdminWithSearch]]
for item in models:
    admin.site.register(*item)
