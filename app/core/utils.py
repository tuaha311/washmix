import os
from pathlib import PosixPath

from django.conf import settings

import phonenumbers
from rest_framework import serializers


def convert_cent_to_dollars(cent_amount: int):
    """
    Converts cents to dollars.
    145 ¢ = 1.45 $
    """

    dollar_amount = cent_amount / settings.CENTS_IN_DOLLAR

    return round(dollar_amount, 2)


def get_dollars(self, attribute_name: str):
    """
    Read a attribute of class instance in cents (¢) and
    transform it to dollars ($).
    """

    cent_amount = getattr(self, attribute_name)

    dollars = convert_cent_to_dollars(cent_amount)

    return dollars


def get_clean_number(raw_number: str):
    """
    In some edge cases in number we have a invalid characters
    or spaces - for this cases we are made some cleanup actions.
    Also, we encapsulated all phone validation logic in this function.

    '+14086660079\u202c' -> '+14086660079‬'
    '+14086660079\u202c\u202c' -> '+14086660079‬‬'
    '+14086660079 ' -> '+14086660079‬‬'
    """

    # provide phone in international format - should start with `+` sign
    if not raw_number.startswith("+"):
        raise serializers.ValidationError(
            detail="Provide number in international format.",
            code="provide_international_format",
        )

    try:
        parsed = phonenumbers.parse(raw_number.strip(), settings.DEFAULT_PHONE_REGION)
    except phonenumbers.NumberParseException:
        raise serializers.ValidationError(
            detail="Invalid phone format.",
            code="invalid_phone_format",
        )

    if not phonenumbers.is_possible_number(parsed):
        raise serializers.ValidationError(
            detail="Invalid phone region.",
            code="invalid_phone_region",
        )

    # extra check for matching country code
    phone_country_code = parsed.country_code
    if phone_country_code not in settings.ALLOWED_COUNTRY_CODES:
        raise serializers.ValidationError(
            detail="Invalid country region.",
            code="invalid_country_region",
        )

    clean_number = phonenumbers.format_number(parsed, settings.DEFAULT_PHONE_FORMAT)

    return clean_number


def clone_from_to(from_object, to_object, exclude_fields: list):
    """
    Clones one object in another.
    """

    for field in from_object._meta.get_fields():
        field_name = field.name

        if field_name in exclude_fields:
            continue

        package_field_value = getattr(from_object, field_name)
        setattr(to_object, field_name, package_field_value)

    return to_object


def exists_in_execution_cache(key: str) -> bool:
    return settings.REDIS_CLIENT.exists(key)


def add_to_execution_cache(key: str, expiration_time: int = settings.REDIS_DEFAULT_EXPIRATION_TIME):
    return settings.REDIS_CLIENT.set(key, 1, ex=expiration_time)


def recursive_getattr(object_, name: str, default=None):
    parts = name.split(".")

    first_element = parts[0]
    rest = parts[1:]

    new_name = ".".join(rest)
    new_object = getattr(object_, first_element, default)

    if not new_name:
        return new_object

    return recursive_getattr(new_object, new_name, default)


def is_file_exists(path: str) -> bool:
    """
    Checks file exists or not.
    """

    return os.path.exists(path)


def ensure_folder_exists(path: PosixPath) -> None:
    """
    We are preparing folder for future usage.
    We should ensure that folder exists - we are always
    trying to create it.
    """

    absolute_path = str(path)

    try:
        os.mkdir(absolute_path)
    except FileExistsError:
        pass


def generate_pdf_report_path(order_pk: int) -> PosixPath:
    """
    Generates PDF-report path for Order.
    """

    pdf_reports_root = settings.PDF_REPORTS_ROOT

    ensure_folder_exists(pdf_reports_root)

    pdf_name = f"order-{order_pk}.pdf"
    pdf_path = pdf_reports_root / pdf_name

    return pdf_path
