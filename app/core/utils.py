from django.conf import settings

import phonenumbers
from rest_framework import serializers


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
    Also, we encapsulated all phone validation logic in this function.

    '+14086660079\u202c' -> '+14086660079‬'
    '+14086660079\u202c\u202c' -> '+14086660079‬‬'
    '+14086660079 ' -> '+14086660079‬‬'
    """

    if not raw_number.startswith("+"):
        raise serializers.ValidationError(
            detail="Provide number in international format.", code="provide_international_format",
        )

    try:
        parsed = phonenumbers.parse(raw_number.strip(), settings.DEFAULT_PHONE_REGION)
    except phonenumbers.NumberParseException:
        raise serializers.ValidationError(
            detail="Invalid phone format.", code="invalid_phone_format",
        )

    if not phonenumbers.is_possible_number(parsed) or not phonenumbers.is_valid_number(parsed):
        raise serializers.ValidationError(
            detail="Invalid phone region.", code="invalid_phone_region",
        )

    clean_number = phonenumbers.format_number(parsed, settings.DEFAULT_PHONE_FORMAT)

    return clean_number
