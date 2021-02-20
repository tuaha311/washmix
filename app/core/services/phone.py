from rest_framework.serializers import Serializer

from core.utils import get_clean_number


class PhoneNumberService:
    def __init__(self, serializer: Serializer):
        self._serializer = serializer

    def cleanup_phone_number(self):
        """
        Method that cleanup phone number and inject
        a clean value into `validated_data`.
        """

        serializer = self._serializer
        validated_data = serializer.validated_data

        if "number" in validated_data:
            raw_phone = validated_data["number"]

            clean_phone = get_clean_number(raw_phone)

            validated_data["number"] = clean_phone

        return serializer
