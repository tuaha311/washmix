from django.contrib import admin
from django.contrib.auth.models import Permission

from core.admin import DefaultAdmin
from users.models import Client, Employee

models = [
    [Client, DefaultAdmin],
    [Employee, DefaultAdmin],
    [Permission],
]
for item in models:
    admin.site.register(*item)
