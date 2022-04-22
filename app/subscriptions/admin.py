from django.contrib import admin

from subscriptions.models import Package, Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    search_fields = ("name",)


models = [Package]
for item in models:
    admin.site.register(item)
admin.site.register(Subscription, SubscriptionAdmin)
