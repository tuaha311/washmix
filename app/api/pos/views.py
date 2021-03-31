from rest_framework.generics import ListAPIView

from api.authentication import default_pos_authentication
from api.permissions import default_pos_permissions
from api.pos.serializers import POSCouponSerializer, POSItemSerializer, POSServiceSerializer
from billing.models import Coupon
from orders.models import Item, Service


class POSItemListView(ListAPIView):
    """
    Method to retrieve all items in POS.
    """

    serializer_class = POSItemSerializer
    queryset = Item.objects.order_by("id")
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions


class POSCouponListView(ListAPIView):
    """
    Method to retrieve all coupons in POS.
    """

    serializer_class = POSCouponSerializer
    queryset = Coupon.objects.all()
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions


class POSServiceListView(ListAPIView):
    """
    Method to retrieve all services with items in POS.
    """

    serializer_class = POSServiceSerializer
    queryset = Service.objects.all().prefetch_related("price_list__item")
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions
