from django.core.exceptions import MultipleObjectsReturned

from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from billing.models import Card
from core.models import Address, Coupon
from modules.constant import MESSAGE_ERROR_MISSING_ADDRESS
from modules.enums import PACKAGES, CouponType
from orders.models import Item, Order


class OrderItemsSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, order=None, data=None, **kwgs):
        self.order = order
        super(OrderItemsSerializer, self).__init__(instance=instance, data=data, **kwgs)

    id = serializers.IntegerField(required=False)

    class Meta:
        model = Item
        fields = ("item", "cost", "id")

    def create(self, validate_data):
        try:
            order_item, _ = Item.objects.get_or_create(
                order=self.order, id=validate_data.get("id") if validate_data.get("id") else None,
            )
        except Item.DoesNotExist:
            raise ValidationError(detail="Not a valid id for an order item")

        for key, value in validate_data.items():
            setattr(order_item, key, value)
        order_item.save()
        return order_item.id


class OrderSerializer(serializers.ModelSerializer):
    """
    Performs following tasks:
    1- Create Orders
    2- Update Orders
    3- Validate order data, receiving from client 
    """

    def __init__(self, instance=None, user=None, data=None, **kwgs):
        self.user = user
        super(OrderSerializer, self).__init__(instance=instance, data=data, **kwgs)

    id = serializers.IntegerField(required=False)
    pick_up_from_datetime = serializers.DateTimeField()
    pick_up_to_datetime = serializers.DateTimeField(required=False)

    drop_off_from_datetime = serializers.DateTimeField()
    drop_off_to_datetime = serializers.DateTimeField(required=False)

    instructions = serializers.CharField(required=False)
    additional_notes = serializers.CharField(required=False)
    next_day_delivery = serializers.BooleanField(required=False)
    same_day_delivery = serializers.BooleanField(required=False)

    order_items = OrderItemsSerializer(many=True)
    card_list = serializers.IntegerField()
    currency = serializers.CharField()

    coupon_code = serializers.CharField(required=False)

    class Meta:
        model = Order
        fields = (
            "user",
            "pick_up_from_datetime",
            "pick_up_to_datetime",
            "drop_off_from_datetime",
            "drop_off_to_datetime",
            "instructions",
            "additional_notes",
            "next_day_delivery",
            "same_day_delivery",
            "count",
            "total_cost",
            "id",
            "order_items",
            "card_list",
            "currency",
            "coupon_code",
        )

    def create(self, validated_data):

        order_items = validated_data.pop("order_items", None)
        currency = validated_data.pop("currency", None)
        wm_card_id = validated_data.pop("card_list", None)
        stripe_status_api = status.HTTP_200_OK
        card = None

        coupon_code = validated_data.pop("coupon_code", None)

        try:
            pickup_addresses = Address.objects.get(user=self.user)
            dropoff_addresses = Address.objects.get(user=self.user)

            # This checks if user has a prepay package
            if not self.user.profile.package_id:
                raise ValidationError(detail="User has not bought package yet")
        except Card.DoesNotExist:
            raise ValidationError(detail="Invalid or no user card added")
        except Address.DoesNotExist:
            raise ValidationError(detail=MESSAGE_ERROR_MISSING_ADDRESS)
        except MultipleObjectsReturned:
            raise ValidationError(detail="Addresses for user Already exist!")

        if coupon_code:
            profile = self.user.profile
            if not profile.is_coupon:
                raise ValidationError(detail="Invalid Coupon Code")
            if PACKAGES.PAYC.value != self.user.profile.package_id.name:
                raise ValidationError(detail="Only PAYC Package is allowed")
            total_cost = validated_data.get("total_cost", 0)
            try:
                coupon = Coupon.objects.get(name=coupon_code, coupon_type=CouponType.FIRST.value)
                if not coupon.valid:
                    raise ValidationError(detail="Not a valid coupon anymore")
            except Coupon.DoesNotExist:
                raise ValidationError(detail="Invalid coupon code")
            discount = coupon.apply_coupon(total_cost)
            profile.is_coupon = False
            profile.save()

            validated_data.update({"discount_amount": discount})

        try:
            if validated_data.get("id"):
                order = Order.objects.get(user=self.user, id=validated_data.get("id"))
            else:
                order = Order.objects.create(
                    user=self.user,
                    pickup_address=pickup_addresses,
                    dropoff_address=dropoff_addresses,
                )
        except Order.DoesNotExist:
            raise ValidationError(detail="Not a valid id for a user order")

        for key, val in validated_data.items():
            setattr(order, key, val)
        order.save()

        order_items_ids = []
        if order_items:
            items_ser = OrderItemsSerializer(many=True, order=order, data=order_items)
            items_ser.is_valid()
            order_items_ids = items_ser.save()
            order.save()

        return (
            {"order_id": order.id, "order_items_ids": order_items_ids},
            stripe_status_api,
        )

    def update(self, instance, validated_data):
        order_items = validated_data.pop("order_items")
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if order_items:
            items_ser = OrderItemsSerializer(many=True, order=instance, data=order_items)
            items_ser.is_valid()
            items_ser.save()

        return instance.id


class OrderHistorySerializer(serializers.ModelSerializer):
    """Maintaining separate serializer for showing user order history"""

    class Meta:
        model = Order
        fields = (
            "user",
            "id",
            "total_cost",
            "count",
            "pick_up_from_datetime",
            "pick_up_to_datetime",
            "drop_off_from_datetime",
            "drop_off_to_datetime",
            "pickup_address",
            "dropoff_address",
            "created",
            "changed",
            "is_paid",
            "order_items",
            "discount_amount",
        )

    order_items = OrderItemsSerializer(many=True)
