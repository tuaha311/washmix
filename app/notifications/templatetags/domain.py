from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def domain():
    return settings.DOMAIN
