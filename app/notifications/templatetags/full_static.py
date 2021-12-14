from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def full_static(path):
    static_url = static(path)

    host = f"{settings.PROTOCOL}://{settings.DOMAIN}"

    return f"{host}{static_url}"


@register.simple_tag
def subtract_value_discount(value, arg):
    return round(value - arg / 100, 1)


@register.simple_tag
def subtract_percentage_discount(value, arg, amount):
    return round(value - (amount / 100) * arg, 1)


@register.simple_tag
def get_percentage_discount(value, arg):
    return round((value / 100) * arg, 1)


@register.simple_tag
def get_value_discount(value, arg):
    return round(arg / 100, 1)
