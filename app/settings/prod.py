"""
Production settings.
"""
from settings.staging import *

# Never leave it as False!
DEBUG = False

WSGI_APPLICATION = "wsgi.prod.application"

# Comment that for WWW not to be prepended.
PREPEND_WWW = True

# This should be set to a list of domains used in production.
ALLOWED_HOSTS = ["..."]

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

COMPRESS_CSS_FILTERS = [
    "compressor.filters.template.TemplateFilter",
    "compressor.filters.css_default.CssAbsoluteFilter",
    "compressor.filters.cssmin.CSSMinFilter",
]

COMPRESS_JS_FILTERS = [
    "compressor.filters.template.TemplateFilter",
    "compressor.filters.jsmin.JSMinFilter",
]

SERVER_EMAIL = "..."

META_SITE_DOMAIN = "..."
