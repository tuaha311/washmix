from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from oauth2_provider.oauth2_validators import AccessToken, Application, Grant, RefreshToken
from rest_framework.authtoken.models import Token
from robots.models import Rule, Url
from social_django.models import Association, Nonce, UserSocialAuth

from api.views.custom import PasswordResetViewCustom


class MyAdminSite(AdminSite):
    def get_urls(self):
        from django.conf.urls import url

        urls = super(MyAdminSite, self).get_urls()
        urls += [
            url(
                r"password_reset/",
                self.admin_view(PasswordResetViewCustom.as_view()),
                name="password_reset",
            )
        ]
        return urls


admin_site = MyAdminSite()


admin_site.register(User, UserAdmin)
admin_site.register(Site)
admin_site.register(Application)
admin_site.register(Grant)
admin_site.register(AccessToken)
admin_site.register(RefreshToken)
admin_site.register(Group)
admin_site.register(Url)
admin_site.register(Rule)
admin_site.register(Token)
admin_site.register(UserSocialAuth)
admin_site.register(Nonce)
admin_site.register(Association)
