from django.contrib.admin.apps import AdminConfig

# class BrandingConfig(AdminConfig):
#     default_site = "branding.site.WashmixAdminSite"
#     name = "branding"
#     default = True
class BrandingConfig(AdminConfig):
    default_site = "branding.site.WashmixAdminSite"