from django.contrib import admin

from billing.models import Card, Transaction, Coupon


admin.site.register(Card)
admin.site.register(Transaction)
admin.site.register(Coupon)
