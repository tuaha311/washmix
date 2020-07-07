from django.contrib.auth.views import PasswordResetView

from api.forms import PasswordResetFormCustom


class PasswordResetViewCustom(PasswordResetView):
    form_class = PasswordResetFormCustom
