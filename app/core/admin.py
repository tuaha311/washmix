from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.models import Group, Permission

from djangoql.admin import DjangoQLSearchMixin
from social_django.models import Association, Nonce, UserSocialAuth


class DefaultAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


registered_models = []
for item in registered_models:
    admin.site.register(*item)

unregistered_models = [Group, Permission, Association, Nonce, UserSocialAuth]
for item in unregistered_models:
    try:
        admin.site.unregister(item)
    except NotRegistered:
        continue
