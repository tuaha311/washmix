from django.contrib.auth.backends import ModelBackend

from api.utils import cleanup_email


class CaseInsensitiveModelBackend(ModelBackend):
    """
    We forced to implement this backend to support case-insensitive login via
    `rest-framework-simplejwt`.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if "email" in kwargs:
            email = kwargs["email"]
            clean_email = cleanup_email(email)
            kwargs["email"] = clean_email

        return super().authenticate(request, username, password, **kwargs)
