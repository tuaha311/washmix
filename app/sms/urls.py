from django.contrib.admin import AdminSite
from django.urls import path

from .views import outbound_sms, send_sms

class ExtraAdminURL(AdminSite):
    def get_urls(self):
        urls = super().get_urls()

        # Add the custom URL patterns for the admin site
        urls += [
            path("sms/outbound-sms/", self.admin_view(outbound_sms), name="outbound_sms"),
        ]

        return urls

# Register your custom admin site
my_admin_site = ExtraAdminURL(name="admin-url")

# Define your app-specific URLs
urlpatterns = [
    path("admin/", my_admin_site.urls),  # Include your custom admin URLs
    path("send-sms/", send_sms, name="send_sms"),
    # Add other app-specific URLs here
]
