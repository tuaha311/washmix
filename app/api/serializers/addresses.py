from rest_framework import serializers

from core.models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            "id",
            "address_line_1",
            "address_line_2",
            "city",
            "zip_code",
            "state",
            "created",
            "changed",
            "title",
        )


class AddressCreateSerializer(serializers.ModelSerializer):
    """
    Serializer responsible of following task
    1- Validating address data from client
    2- Updating address data
    3- Creating address
    """

    def __init__(self, instance=None, user=None, data=None, **kwgs):
        self.user = user
        super(AddressCreateSerializer, self).__init__(instance=instance, data=data, **kwgs)

    id = serializers.IntegerField(required=False)
    address_line_1 = serializers.CharField(allow_blank=True)
    address_line_2 = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(allow_blank=True)
    state = serializers.CharField(allow_blank=True)
    zip_code = serializers.CharField(allow_blank=True)
    title = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Address
        fields = (
            "id",
            "address_line_1",
            "city",
            "state",
            "zip_code",
            "address_line_2",
            "title",
        )


# LEGACY
class PickupAddressSerializer(AddressCreateSerializer):
    pass


# LEGACY
class DropoffAddressSerializer(AddressCreateSerializer):
    pass


# LEGACY
class AddressGetSerializer(AddressSerializer):
    pass


# LEGACY
class DropoffAddressGetSerializer(AddressSerializer):
    pass
