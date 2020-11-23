from django.contrib.admin.apps import AdminConfig


class OtherConfig(AdminConfig):
    default_site = "other.site.WashmixAdminSite"
