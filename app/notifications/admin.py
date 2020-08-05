from django.contrib import admin

from notifications.models import Notification

models = [Notification]
for item in models:
    admin.site.register(item)
