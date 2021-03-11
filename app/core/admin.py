from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.models import Permission

from djangoql.admin import DjangoQLSearchMixin
from social_django.models import Association, Nonce, UserSocialAuth

from core.mixins import AdminUpdateFieldsMixin
from core.models import Phone


class AdminWithSearch(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


class PhoneAdmin(AdminUpdateFieldsMixin, AdminWithSearch):
    pass


registered_models = [[Phone, PhoneAdmin]]
for item in registered_models:
    admin.site.register(*item)

unregistered_models = [Permission, Association, Nonce, UserSocialAuth]
for item in unregistered_models:
    try:
        admin.site.unregister(item)
    except NotRegistered:
        continue
