from django.contrib import admin

from djangoql.admin import DjangoQLSearchMixin

from core.models import Phone

admin.site.site_header = "Washmix"
admin.site.site_title = "washmix.com"
admin.site.index_title = "Washmix Admin Panel"


class DefaultAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


models = [[Phone, DefaultAdmin]]
for item in models:
    admin.site.register(*item)
