from django.conf import settings
from django.core.exceptions import ValidationError

import phonenumbers


def validate_phone(value):
    if value.startswith("+"):
        raise ValidationError("Provide phone number without + sign", code="dont_provide_plus")

    try:
        phonenumbers.parse(value, region=settings.DEFAULT_PHONE_REGION)
    except phonenumbers.NumberParseException:
        raise ValidationError("You have provided invalid region for phone", code="invalid_region")
