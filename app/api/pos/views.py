from rest_framework.generics import ListAPIView

from api.authentication import default_pos_authentication
from api.permissions import default_pos_permissions
from api.pos.serializers import POSCouponSerializer, POSItemSerializer
from billing.models import Coupon
from orders.models import Item


class POSItemListView(ListAPIView):
    serializer_class = POSItemSerializer
    queryset = Item.objects.order_by("id")
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions


class POSCouponListView(ListAPIView):
    serializer_class = POSCouponSerializer
    queryset = Coupon.objects.all()
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions
