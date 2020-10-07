from django.contrib import admin

from billing.models import Card, Coupon, Transaction

models = [Card, Transaction, Coupon]
for item in models:
    admin.site.register(item)
