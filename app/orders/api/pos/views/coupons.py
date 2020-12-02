from api.authentication import default_pos_authentication
from api.permissions import default_pos_permissions
from orders.api.client.views.coupons import OrderApplyCouponView
from orders.models import Order


class POSOrderApplyCouponView(OrderApplyCouponView):
    authentication_classes = default_pos_authentication
    permission_classes = default_pos_permissions

    def get_client(self, order: Order):
        client = order.client
        return client
