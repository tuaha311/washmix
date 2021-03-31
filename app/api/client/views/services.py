from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from api.client.serializers.services import ServiceSerializer
from orders.models import Service


class ServiceListView(ListAPIView):
    """
    PUBLIC METHOD.

    Retrieve a list of services for items with prices.
    """

    permission_classes = [AllowAny]
    serializer_class = ServiceSerializer
    queryset = Service.objects.all().prefetch_related("price_list__item")
