from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User

from social_django.models import Association, Nonce, UserSocialAuth

admin_site = AdminSite()


admin_site.register(User, UserAdmin)
admin_site.register(Group)
admin_site.register(UserSocialAuth)
admin_site.register(Nonce)
admin_site.register(Association)
