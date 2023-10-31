# deliveries/decorators.py

from functools import wraps
from django.http import HttpResponseForbidden

def has_permission(perm_codename):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.has_perm(perm_codename):
                print("ACCESS GRANTED")
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("You don't have permission to access this page.")
        return _wrapped_view
    return decorator