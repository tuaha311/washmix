from django.contrib import admin
from django.contrib.auth.models import Permission

from users.models import Profile

models = [
    Profile,
    Permission,
]
for item in models:
    admin.site.register(item)
