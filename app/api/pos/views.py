from rest_framework.generics import ListAPIView

from api.permissions import default_pos_permissions
from api.pos.serializers import CouponSerializer, ItemSerializer
from billing.models import Coupon
from orders.models import Item


class ItemListView(ListAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.order_by("id")
    permission_classes = default_pos_permissions


class CouponListView(ListAPIView):
    serializer_class = CouponSerializer
    queryset = Coupon.objects.all()
    permission_classes = default_pos_permissions
