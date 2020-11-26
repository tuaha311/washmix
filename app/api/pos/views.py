from rest_framework.generics import ListAPIView

from api.permissions import default_pos_permissions
from api.pos.serializers import ItemSerializer
from orders.models import Item


class ItemListView(ListAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.order_by("id")
    permission_classes = default_pos_permissions
