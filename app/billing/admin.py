from django.contrib import admin

from billing.models import Card, Coupon, Package, Transaction

models = [Card, Transaction, Coupon, Package]
for item in models:
    admin.site.register(item)
