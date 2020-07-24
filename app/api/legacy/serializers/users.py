from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from api.fields import EnumField
from api.legacy.serializers.addresses import (
    AddressGetSerializer,
    DropoffAddressGetSerializer,
    DropoffAddressSerializer,
    PickupAddressSerializer,
)
from api.legacy.serializers.orders import OrderHistorySerializer, OrderSerializer
from billing.models import Card
from core.models import Package
from modules.enums import AppUsers, Crease, Detergents, SignUp, Starch
from modules.helpers import commit_transaction, random_string
from users.models import Client


def email_validator(value):
    try:
        user = User.objects.get(email=value)
        if user and user.client.authentication_provider == SignUp.washmix.value:
            raise ValidationError({"email": "User already exist!"})
        raise ValidationError(
            {
                "email": "User already signed up with {0}".format(
                    user.client.authentication_provider
                )
            }
        )
    except User.DoesNotExist:
        pass


def phone_validator():
    return RegexValidator(regex=r"^\d{7,15}$", message="7 to 10 digits allowed.")


class UserListSerializer(serializers.ListSerializer):
    """
    Serializer responsible for following tasks:
    1- Updating user records in bulk.
    """

    def update(self, user_instance, validated_data):
        """
        :param user_instance: User instance which needs to be updated 
        :param validated_data: User related data which is being validated 
        by corresponding serializer.
        :return: Dict: containing user id and list of address ids.
        """
        validated_data = validated_data[0]
        pickup_addresses = validated_data.pop("pickup_addresses", None)
        dropoff_addresses = validated_data.pop("dropoff_addresses", None)
        orders = validated_data.pop("orders", None)
        client = validated_data.pop("client", None)

        # User client update
        user = None
        if validated_data.get("user_id"):
            try:
                user = User.objects.get(id=validated_data.pop("user_id"))
            except User.DoesNotExist:
                user = user_instance
            if not user_instance.is_staff:
                if user_instance != user:
                    raise PermissionDenied()
            user_instance = user

        if client:
            if client.get("app_users") == AppUsers.POTENTIAL_USERS.value:
                validated_data.update({"password": make_password(random_string())})
                validated_data.update({"is_active": False})

            package = client.pop("package", None)
            name = client.pop("name", None)

            profile_db, _ = Client.objects.get_or_create(user=user_instance)

            for pref, val in client.items():
                setattr(profile_db, pref, val)

            if package or name:
                kwargs = {}
                kwargs.update({"id": package} if package else {"name": name})
                try:
                    setattr(profile_db, "package", Package.objects.get(**kwargs))
                except Package.DoesNotExist:
                    raise ValidationError(detail="Wrong Package name or id")
            profile_db.save()

        # User update
        for key, value in validated_data.items():
            if key == "password":
                value = make_password(validated_data["password"])
            elif key == "email":
                setattr(user_instance, "username", value)
            setattr(user_instance, key, value)
        user_instance.save()

        # Address update
        order_status = {}
        if pickup_addresses:
            address_ser = PickupAddressSerializer(
                many=True, user=user_instance, data=pickup_addresses, partial=True
            )
            address_ser.is_valid()
            order_status.update(
                {"pickup_address": AddressGetSerializer(address_ser.save(), many=True).data}
            )

        if dropoff_addresses:
            address_ser = DropoffAddressSerializer(
                many=True, user=user_instance, data=dropoff_addresses, partial=True
            )
            address_ser.is_valid()
            order_status.update(
                {"dropoff_address": DropoffAddressGetSerializer(address_ser.save(), many=True).data}
            )

        if orders:
            order_ser = OrderSerializer(
                user=user_instance,
                data=orders,
                partial=True,
                context={"request": self.context["request"]},
            )
            order_ser.is_valid()
            order_status, stripe_status = order_ser.save()
            order_status.update(order_status)
            order_status.update({"message": stripe_status})

        response = {"user": user_instance.id}
        response.update(order_status)
        return response


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer responsible for following tasks:
    1- Creating User Record
    2- Validating user Record
    """

    email = serializers.EmailField(validators=[email_validator])
    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)
    phone = serializers.CharField(
        validators=[phone_validator()], source="client.phone", allow_blank=True
    )
    package = serializers.IntegerField(source="client.package", required=False, allow_null=True)
    name = serializers.CharField(source="client.name", required=False, allow_blank=True)
    password = serializers.CharField(required=False)

    # Preferences
    detergents = EnumField(enum=Detergents, source="client.detergents", required=False)
    starch = EnumField(enum=Starch, source="client.starch", required=False)
    no_crease = EnumField(enum=Crease, source="client.no_crease", required=False)
    fabric_softener = serializers.BooleanField(source="client.fabric_softener", required=False)
    fix_tears = serializers.BooleanField(source="client.fix_tears", required=False)

    app_users = EnumField(enum=AppUsers, source="client.app_users", required=False)

    # Employee
    DOB = serializers.DateField(source="client.DOB", required=False)
    joining_date = serializers.DateField(source="client.joining_date", required=False)
    SSN = serializers.CharField(source="client.SSN", required=False)

    # Customer
    is_doormen = serializers.BooleanField(source="client.is_doormen", required=False)

    pickup_addresses = PickupAddressSerializer(many=True, required=False)
    dropoff_addresses = DropoffAddressSerializer(many=True, required=False)
    orders = OrderSerializer(required=False)
    is_staff = serializers.BooleanField(required=False, default=False)
    user_id = serializers.IntegerField(required=False)
    # user_purchases = UserPurchasesSerializer(many=True, required=False)

    class Meta:
        model = User
        list_serializer_class = UserListSerializer
        fields = (
            "url",
            "email",
            "first_name",
            "last_name",
            "password",
            "phone",
            "pickup_addresses",
            "dropoff_addresses",
            "orders",
            "package",
            "name",
            "is_staff",
            "user_id",
            "detergents",
            "starch",
            "no_crease",
            "fabric_softener",
            "fix_tears",
            "app_users",
            "DOB",
            "joining_date",
            "SSN",
            "is_doormen",
        )

    def validate(self, attrs):
        if (
            attrs.get("is_staff")
            and attrs.get("client").get("app_users") == AppUsers.EMPLOYEE.value
        ):
            raise ValidationError(detail="User cannot be admin and employee at the same time")
        return attrs

    def create(self, validated_data):
        """
        :param validated_data: 
        :return: Dict: Containing user Id and list of address Ids. 
        """
        pickup_address = None
        dropoff_address = None
        if validated_data.get("pickup_addresses"):
            pickup_address = validated_data.pop("pickup_addresses")
        if validated_data.get("dropoff_addresses"):
            dropoff_address = validated_data.pop("dropoff_addresses")

        client = validated_data.pop("client", None)
        validated_data.update(
            {
                "password": make_password(random_string())
                if client.get("app_users")
                else make_password(validated_data.get("password", "")),
                "username": validated_data["email"],
            }
        )

        if client.get("app_users", AppUsers.REGULAR_USERS.value) == AppUsers.POTENTIAL_USERS.value:
            validated_data.update({"is_active": False})

        user = User(**validated_data)
        commit_transaction(user)
        # Since 'phone' field is not available in auth_user table
        # therefore handled it separately in client model
        Client.objects.create(user=user, **client)

        resultant = {}
        if pickup_address:
            address_ser = PickupAddressSerializer(many=True, user=user, data=pickup_address)
            address_ser.is_valid()
            resultant.update(
                {"pickup_address": AddressGetSerializer(address_ser.save(), many=True).data}
            )
        if dropoff_address:
            address_ser = DropoffAddressSerializer(many=True, user=user, data=dropoff_address)
            address_ser.is_valid()
            resultant.update(
                {"dropoff_address": DropoffAddressGetSerializer(address_ser.save(), many=True).data}
            )

        response = {"user": user.id}
        response.update(resultant)
        return response


class PackageTypeSerializer(serializers.ModelSerializer):
    """
    Serializer which maps user package to user.    
    """

    class Meta:
        model = Package
        fields = ("name",)


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer which adds in more info to user object.
    """

    class Meta:
        model = Client
        fields = (
            "phone",
            "package",
            "user_package",
            "balance",
            "detergents",
            "starch",
            "no_crease",
            "fabric_softener",
            "fix_tears",
            "stripe_customer_id",
            "authentication_provider",
            "DOB",
            "joining_date",
            "SSN",
            "is_doormen",
            "app_users",
        )

    user_package = PackageTypeSerializer(source="package", read_only=True)


class UserCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = (
            "id",
            "stripe_card_id",
            "is_active",
        )


class UserDataSerializer(serializers.ModelSerializer):
    """
    Serializer which declares format for json in case of getting users information
    """

    def __init__(self, instance=None, stripes_helper=None, **kwargs):
        self.stripe_helper = stripes_helper
        if self.stripe_helper:
            self.stripe_helper.load_strip_api()
        super(UserDataSerializer, self).__init__(instance=instance, **kwargs)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "pickupaddress",
            "dropoffaddress",
            "client",
            "order",
            "card_list",
            "is_staff",
        )

    def to_representation(self, obj):
        """This function helps us renaming default name defined in serializer field list.
            
        Since address and client is a valid name for models therefore we renamed them
        while serializing json"""

        primitive_repr = super(UserDataSerializer, self).to_representation(obj)

        primitive_profile_repr = primitive_repr["client"]

        primitive_repr["pickup_addresses"] = (
            primitive_repr["pickupaddress"] if primitive_repr["pickupaddress"] else None
        )
        primitive_repr["dropoff_addresses"] = (
            primitive_repr["dropoffaddress"] if primitive_repr["dropoffaddress"] else None
        )

        if primitive_profile_repr:
            primitive_repr["authentication_provider"] = primitive_profile_repr[
                "authentication_provider"
            ]
            primitive_repr["phone"] = primitive_profile_repr["phone"]
            primitive_repr["balance"] = primitive_profile_repr["balance"]
            primitive_repr["detergents"] = primitive_profile_repr["detergents"]
            primitive_repr["starch"] = primitive_profile_repr["starch"]
            primitive_repr["fix_tears"] = primitive_profile_repr["fix_tears"]
            primitive_repr["no_crease"] = primitive_profile_repr["no_crease"]
            primitive_repr["fabric_softener"] = primitive_profile_repr["fabric_softener"]
            primitive_repr["package"] = primitive_profile_repr["package"]

            # Employee
            primitive_repr["DOB"] = primitive_profile_repr["DOB"]
            primitive_repr["joining_date"] = primitive_profile_repr["joining_date"]
            primitive_repr["SSN"] = primitive_profile_repr["SSN"]

            # Customer
            primitive_repr["is_doormen"] = primitive_profile_repr["is_doormen"]

            primitive_repr["app_users"] = primitive_profile_repr["app_users"]

            primitive_repr["name"] = (
                primitive_profile_repr["user_package"]["name"]
                if primitive_profile_repr["user_package"]
                else ""
            )

            if primitive_repr.get("card_list"):
                try:
                    if not self.stripe_helper.customer:
                        self.stripe_helper.get_customer(obj)

                    for card in primitive_repr.get("card_list"):
                        card_prop = self.stripe_helper.get_card_info(card["stripe_card_id"])
                        card.update(
                            {
                                "cvc": card_prop.cvc_check,
                                "exp_year": card_prop.exp_year,
                                "exp_month": card_prop.exp_month,
                                "last4": card_prop.last4,
                            }
                        )
                except AttributeError:
                    pass

        primitive_repr.pop("pickupaddress", None)
        primitive_repr.pop("dropoffaddress", None)
        primitive_repr.pop("client")
        return primitive_repr

    pickupaddress = AddressGetSerializer(many=True, read_only=True)
    dropoffaddress = DropoffAddressGetSerializer(many=True, read_only=True)
    order = OrderHistorySerializer(many=True, read_only=True)
    client = ProfileSerializer(read_only=True)
    card_list = UserCardSerializer(many=True)
