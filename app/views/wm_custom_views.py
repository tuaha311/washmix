from django.contrib.auth.views import PasswordResetView
from rest_framework.permissions import IsAdminUser

from ..forms.custom_forms import PasswordResetFormCustom


class PasswordResetViewCustom(PasswordResetView):
    form_class = PasswordResetFormCustom
