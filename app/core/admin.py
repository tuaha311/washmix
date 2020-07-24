from django.contrib import admin

from core.models import Address, Notification, Package, Product, Phone, ZipCode

admin.site.site_header = "Washmix"
admin.site.site_title = "washmix.com"
admin.site.index_title = "Washmix Admin Panel"

models = [Package, Product, Address, Notification, Phone, ZipCode]
for item in models:
    admin.site.register(item)
