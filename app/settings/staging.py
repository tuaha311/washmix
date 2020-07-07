"""
Staging settings.
"""
from settings.base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

WSGI_APPLICATION = "wsgi.staging.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "wm_django_staging",
        "USER": "wm_django_staging",
        "PASSWORD": "",
    }
}

COMPRESS_ENABLED = True

COMPRESS_CSS_FILTERS = [
    "compressor.filters.template.TemplateFilter",
    "compressor.filters.css_default.CssAbsoluteFilter",
    "compressor.filters.cssmin.CSSMinFilter",
]

COMPRESS_JS_FILTERS = [
    "compressor.filters.template.TemplateFilter",
    "compressor.filters.jsmin.JSMinFilter",
]
