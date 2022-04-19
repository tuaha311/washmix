from django import forms
from django.contrib import admin
from django.db.models import Q

from core.admin import AdminWithSearch
from core.mixins import AdminUpdateFieldsMixin
from locations.models import Address, City, ZipCode
from users.admin import CustomAutocompleteSelect


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = "__all__"

        widgets = {
            "client": CustomAutocompleteSelect(
                model._meta.get_field("client").remote_field, "Select a Client", admin.site
            ),
            "zip_code": CustomAutocompleteSelect(
                model._meta.get_field("zip_code").remote_field, "Select a Zip Code", admin.site
            ),
        }


class AddressAdmin(AdminUpdateFieldsMixin, AdminWithSearch):
    form = AddressForm

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if "autocomplete" in request.path:
            queryset = queryset.filter(
                Q(address_line_1__icontains=request.GET.get("q", ""))
                | Q(address_line_2__icontains=request.GET.get("q", ""))
                | Q(zip_code__value__icontains=request.GET.get("q", ""))
            )
        return queryset, use_distinct


models = [[ZipCode, AdminWithSearch], [City, AdminWithSearch], [Address, AddressAdmin]]
for item in models:
    admin.site.register(*item)
