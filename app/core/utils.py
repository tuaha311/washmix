from django.conf import settings

import phonenumbers


def get_dollars(self, attribute_name):
    amount_value = getattr(self, attribute_name)
    return amount_value / settings.CENTS_IN_DOLLAR


def cleanup_number(phone):
    """
    '+14086660079‬' -> '+14086660079\u202c'
    '+14086660079‬‬' -> '+14086660079\u202c\u202c'
    """

    parsed = phonenumbers.parse(phone)
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
