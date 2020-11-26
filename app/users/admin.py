from django.contrib import admin

from core.admin import DefaultAdmin
from deliveries.admin import RequestInline
from users.models import Client, Customer, Employee


class ClientAdmin(DefaultAdmin):
    inlines = [RequestInline]


models = [
    [Client, ClientAdmin],
    [Employee, DefaultAdmin],
    [Customer, DefaultAdmin],
]
for item in models:
    admin.site.register(*item)
