import pytest
from rest_framework.serializers import ValidationError

from core.utils import get_clean_number


def test_invalid_phone_numbers():
    phones = [
        # 1
        "1",
        "123",
        "1234528347920384792387469",
        "+1283472934623984762384762386",
        # 3
        "3",
        "333",
        "32863",
        "3927412",
        "3*&@#^$",
        "+3853",
        # 6
        "654",
        "612945",
        "69805245",
        "6iufsafg6i7",
        # 7
        "789",
        "78902",
        "+7926183",
        "+792641845",
        "+7283974934tr76t34ru6734282",
    ]

    for item in phones:
        with pytest.raises(ValidationError):
            get_clean_number(item)


def test_valid_phone_numbers():
    phones = [
        "+14132994663",
        "+14153992233",
    ]

    for item in phones:
        clean_number = get_clean_number(item)
        assert clean_number == item
