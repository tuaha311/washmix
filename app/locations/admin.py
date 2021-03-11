from django.contrib import admin

from core.admin import AdminWithSearch
from core.mixins import AdminUpdateFieldsMixin
from locations.models import Address, City, ZipCode


class AddressAdmin(AdminUpdateFieldsMixin, AdminWithSearch):
    pass


models = [[ZipCode, AdminWithSearch], [City, AdminWithSearch], [Address, AddressAdmin]]
for item in models:
    admin.site.register(*item)
