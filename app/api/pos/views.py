from rest_framework.generics import ListAPIView

from api.permissions import default_permissions_for_admin
from api.pos.serializers import ItemSerializer
from orders.models import Item


class ItemListView(ListAPIView):
    permission_classes = default_permissions_for_admin
    serializer_class = ItemSerializer
    queryset = Item.objects.order_by("id")
