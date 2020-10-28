from rest_framework.generics import ListAPIView

from locations.api.serializers.zip_codes import ZipCodeSerializer
from locations.models import ZipCode


class ZipCodeListView(ListAPIView):
    serializer_class = ZipCodeSerializer
    queryset = ZipCode.objects.all()
