from django.test import override_settings

import pytest
from rest_framework.serializers import ValidationError

from core.utils import get_clean_number


@override_settings(ALLOWED_COUNTRY_CODES=["US"])
def test_invalid_phone_numbers():
    phones = [
        # 1 (USA, Canada)
        "1",
        "123",
        "1234528347920384792387469",
        "+1283472934623984762384762386",
        # 44 (United Kingdom)
        "440",
        "44999",
        "4432344",
        "+4429837",
        "+447855565905",  # fake phone
        # 46 (Sweden)
        "46",
        "463",
        "46863",
        "4627412",
        "46*&@#^$",
        "+4653",
        "+46392193",
        "+467855587",  # fake phone
        # 6 (None)
        "654",
        "612945",
        "69805245",
        "6iufsafg6i7",
        # 7 (Russia)
        "789",
        "78902",
        "+7926183",
        "+792641845",
        "+79055558309",  # fake phone
        "+7283974934tr76t34ru6734282",
    ]

    for item in phones:
        with pytest.raises(ValidationError):
            get_clean_number(item)


@override_settings(ALLOWED_COUNTRY_CODES=["US"])
def test_valid_phone_numbers():
    phones = [
        "+14132994663",
        "+14153992233",
    ]

    for item in phones:
        clean_number = get_clean_number(item)
        assert clean_number == item
