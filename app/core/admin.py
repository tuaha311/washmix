from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.models import Permission
from django.db.models import Q

from djangoql.admin import DjangoQLSearchMixin
from social_django.models import Association, Nonce, UserSocialAuth

from core.mixins import AdminUpdateFieldsMixin
from core.models import Phone


class AdminWithSearch(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


class PhoneAdmin(AdminUpdateFieldsMixin, AdminWithSearch):
    autocomplete_fields = ("client",)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if "autocomplete" in request.path:
            queryset = queryset.filter(
                Q(client__user__email__icontains=request.GET.get("q", ""))
                | Q(number__icontains=request.GET.get("q", ""))
            )
        return queryset, use_distinct


registered_models = [[Phone, PhoneAdmin]]
for item in registered_models:
    admin.site.register(*item)

unregistered_models = [Permission, Association, Nonce, UserSocialAuth]
for item in unregistered_models:
    try:
        admin.site.unregister(item)
    except NotRegistered:
        continue
