from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from api.v1_0.serializers.locations import LocationSerializer
from locations.models import City


class LocationViewList(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = LocationSerializer
    queryset = City.objects.all()
