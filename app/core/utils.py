from django.conf import settings


def get_dollars(self, attribute_name):
    amount_value = getattr(self, attribute_name)
    return amount_value / settings.CENTS_IN_DOLLAR
