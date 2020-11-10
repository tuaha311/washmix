from django.contrib import admin

from core.admin import DefaultAdmin
from users.models import Client, Customer, Employee

models = [
    [Client, DefaultAdmin],
    [Employee, DefaultAdmin],
    [Customer, DefaultAdmin],
]
for item in models:
    admin.site.register(*item)
