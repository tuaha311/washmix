from rest_framework.generics import ListAPIView

from locations.models import ZipCode
from locations.serializers.zip_codes import ZipCodeSerializer


class ZipCodeListView(ListAPIView):
    serializer_class = ZipCodeSerializer
    queryset = ZipCode.objects.all()
