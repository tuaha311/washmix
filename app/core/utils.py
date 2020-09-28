from django.conf import settings

import phonenumbers


def get_dollars(self, attribute_name: str):
    """
    Returns amount in dollars.
    """
    amount_value = getattr(self, attribute_name)
    return amount_value / settings.CENTS_IN_DOLLAR


def get_clean_number(raw_number: str):
    """
    In some edge cases in number we have a invalid characters
    or spaces - for this cases we are made some cleanup actions.

    '+14086660079\u202c' -> '+14086660079‬'
    '+14086660079\u202c\u202c' -> '+14086660079‬‬'
    '+14086660079 ' -> '+14086660079‬‬'
    """

    parsed = phonenumbers.parse(raw_number.strip(), settings.DEFAULT_PHONE_REGION)
    clean_number = phonenumbers.format_number(parsed, settings.DEFAULT_PHONE_FORMAT)

    return clean_number
