from django.utils import timezone
from django.conf import settings

def expired(created):
    """Return boolean indicating token expiration."""
    now = timezone.now()
    if created < now - settings.EXTENDED_TOKEN_LIFESPAN:
        return True
    return False
