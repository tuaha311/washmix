from settings.base import *

DEBUG = False

PREPEND_WWW = True

ALLOWED_HOSTS = ["*"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
    }
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.",
        "NAME": "wm_django_prod",
        "USER": "wm_django_prod",
        "PASSWORD": "",
    }
}
