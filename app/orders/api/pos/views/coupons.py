from api.authentication import default_pos_authentication
from api.permissions import default_pos_permissions
from orders.api.client.views.coupons import OrderApplyCouponView, OrderRemoveCouponView
from orders.api.pos.serializers.coupons import (
    POSOrderApplyCouponSerializer,
    POSOrderRemoveCouponSerializer,
)


class POSOrderApplyCouponView(OrderApplyCouponView):
    serializer_class = POSOrderApplyCouponSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions


class POSOrderRemoveCouponView(OrderRemoveCouponView):
    serializer_class = POSOrderRemoveCouponSerializer
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions
