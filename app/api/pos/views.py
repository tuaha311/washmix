from rest_framework.generics import ListAPIView

from api.authentication import default_pos_authentication
from api.permissions import default_pos_permissions
from api.pos.serializers import CouponSerializer, ItemSerializer
from billing.models import Coupon
from orders.models import Item


class ItemListView(ListAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.order_by("id")
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions


class CouponListView(ListAPIView):
    serializer_class = CouponSerializer
    queryset = Coupon.objects.all()
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions
