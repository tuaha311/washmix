from models.models import DropoffAddress, PickupAddress
from rest_framework import serializers


class PickupAddressSerializer(serializers.ModelSerializer):
    """
    Serializer responsible of following task
    1- Validating address data from client
    2- Updating address data
    3- Creating address
    """

    def __init__(self, instance=None, user=None, data=None, **kwgs):
        self.user = user
        super(PickupAddressSerializer, self).__init__(instance=instance, data=data, **kwgs)

    id = serializers.IntegerField(required=False)
    address_line_1 = serializers.CharField(allow_blank=True)
    address_line_2 = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(allow_blank=True)
    state = serializers.CharField(allow_blank=True)
    zip_code = serializers.CharField(allow_blank=True)
    title = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = PickupAddress
        fields = (
            "id",
            "address_line_1",
            "city",
            "state",
            "zip_code",
            "address_line_2",
            "title",
        )

    def create(self, validate_data):
        if validate_data.get("id"):
            address, created = PickupAddress.objects.get_or_create(
                user=self.user, id=validate_data.get("id")
            )
        else:
            address = PickupAddress.objects.create(user=self.user)
        for key, value in validate_data.items():
            setattr(address, key, value)
        address.save()
        return address


class DropoffAddressSerializer(serializers.ModelSerializer):
    """
    Serializer responsible of following task
    1- Validating address data from client
    2- Updating address data
    3- Creating address
    """

    def __init__(self, instance=None, user=None, data=None, **kwgs):
        self.user = user
        super(DropoffAddressSerializer, self).__init__(instance=instance, data=data, **kwgs)

    id = serializers.IntegerField(required=False)
    address_line_1 = serializers.CharField(allow_blank=True)
    address_line_2 = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(allow_blank=True)
    state = serializers.CharField(allow_blank=True)
    zip_code = serializers.CharField(allow_blank=True)
    title = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = DropoffAddress
        fields = (
            "id",
            "address_line_1",
            "city",
            "state",
            "zip_code",
            "address_line_2",
            "title",
        )

    def create(self, validate_data):
        if validate_data.get("id"):
            address, created = DropoffAddress.objects.get_or_create(
                user=self.user, id=validate_data.get("id")
            )
        else:
            address = DropoffAddress.objects.create(user=self.user)
        for key, value in validate_data.items():
            setattr(address, key, value)
        address.save()
        return address


class AddressGetSerializer(serializers.ModelSerializer):
    """
    Serializer declares format for json in case of getting user's address 
    """

    class Meta:
        model = PickupAddress
        fields = (
            "id",
            "address_line_1",
            "address_line_2",
            "city",
            "zip_code",
            "state",
            "added_datetime",
            "updated_datetime",
            "title",
        )


class DropoffAddressGetSerializer(serializers.ModelSerializer):
    """
    Serializer declares format for json in case of getting user's address 
    """

    class Meta:
        model = DropoffAddress
        fields = (
            "id",
            "address_line_1",
            "address_line_2",
            "city",
            "zip_code",
            "state",
            "added_datetime",
            "updated_datetime",
            "title",
        )
