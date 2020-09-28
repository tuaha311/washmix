from django.core import exceptions as db_exceptions

from rest_framework import serializers as rest_exceptions

from core.utils import get_clean_number


def validate_phone(value: str):
    try:
        get_clean_number(value)
    except rest_exceptions.ValidationError:
        raise db_exceptions.ValidationError(
            "You have provided invalid region for phone", code="invalid_region"
        )
