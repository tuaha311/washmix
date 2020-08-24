from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def twitter_url():
    return settings.TWITTER_URL


@register.simple_tag
def instagram_url():
    return settings.INSTAGRAM_URL


@register.simple_tag
def facebook_url():
    return settings.FACEBOOK_URL
