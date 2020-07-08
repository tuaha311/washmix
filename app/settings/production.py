from settings.base import *

DEBUG = False

WSGI_APPLICATION = "settings.wsgi.application"

PREPEND_WWW = True

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
