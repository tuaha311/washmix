from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from api.v1_0.serializers.locations import LocationSerializer
from locations.models import City


class LocationListView(ListAPIView):
    """
    PUBLIC METHOD.

    Retrieve a list of cities where we work and list of
    valid zip codes that we support.
    """

    permission_classes = [AllowAny]
    serializer_class = LocationSerializer
    queryset = City.objects.all()
