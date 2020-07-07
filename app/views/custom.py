from django.contrib.auth.views import PasswordResetView

from forms.custom_forms import PasswordResetFormCustom


class PasswordResetViewCustom(PasswordResetView):
    form_class = PasswordResetFormCustom
