from django.contrib import admin

from core.models import Phone

admin.site.site_header = "Washmix"
admin.site.site_title = "washmix.com"
admin.site.index_title = "Washmix Admin Panel"

models = [Phone]
for item in models:
    admin.site.register(item)
