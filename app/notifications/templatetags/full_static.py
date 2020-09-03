from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def full_static(path):
    static_url = static(path)

    host = f"{settings.PROTOCOL}://{settings.DOMAIN}"

    return f"{host}{static_url}"
