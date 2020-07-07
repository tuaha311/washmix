from core.models import Profile
from django.contrib.auth.models import User


def add_additional_social_userinfo(*args, **kwargs):
    if kwargs["is_new"]:
        user = kwargs["user"]
        user.username = getattr(user, "email") or getattr(user, "username")
        user.save()
        Profile.objects.create(user=user, authentication_provider=kwargs.get("backend").name)
    return None


def check_email_exists(backend, details, uid, user=None, *args, **kwargs):
    email = details.get("email") or kwargs.get("username")
    try:
        user = User.objects.get(username=email)
        if not user.last_name:
            user.last_name = details.get("last_name", "") or kwargs.get("last_name", "")
        if not user.first_name:
            user.first_name = details.get("first_name", "") or kwargs.get("first_name", "")
        user.save()
        return user
    except User.DoesNotExist:
        pass
