from django import template
from django.conf import settings
from django.templatetags.static import static

from billing.services.coupon import CouponService

register = template.Library()


@register.simple_tag
def full_static(path):
    static_url = static(path)

    host = f"{settings.PROTOCOL}://{settings.DOMAIN}"

    return f"{host}{static_url}"


@register.simple_tag
def subtract_coupon_discount(amount, coupon, value):
    coupon_service = CouponService(amount * 100, coupon)
    coupon_discount = coupon_service.calculate_coupon_discount()
    return round(value - coupon_discount / 100, 2)


@register.simple_tag
def get_coupon_discount(amount, coupon):
    coupon_service = CouponService(amount * 100, coupon)
    coupon_discount = coupon_service.calculate_coupon_discount()
    return round(coupon_discount / 100, 2)
