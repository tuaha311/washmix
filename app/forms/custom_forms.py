from django.contrib.auth.forms import PasswordResetForm

from django import forms
from django.contrib.auth.models import User


def email_validator(value):
    try:
        user = User.objects.get(email=value)
        if not (user.is_active and user.is_staff):
            raise forms.ValidationError(message='User must be a staff')
    except User.DoesNotExist:
        pass
    return True


class PasswordResetFormCustom(PasswordResetForm):
    email = forms.EmailField(validators=[email_validator])