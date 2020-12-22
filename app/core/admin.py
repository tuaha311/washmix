from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.models import Permission

from djangoql.admin import DjangoQLSearchMixin
from social_django.models import Association, Nonce, UserSocialAuth

from core.models import Phone


class DefaultAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


registered_models = [[Phone, DefaultAdmin]]
for item in registered_models:
    admin.site.register(*item)

unregistered_models = [Permission, Association, Nonce, UserSocialAuth]
for item in unregistered_models:
    try:
        admin.site.unregister(item)
    except NotRegistered:
        continue
