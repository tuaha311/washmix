from rest_framework.generics import ListAPIView

from api.v1_0.serializers.zip_codes import ZipCodeSerializer
from locations.models import ZipCode


class ZipCodeListView(ListAPIView):
    serializer_class = ZipCodeSerializer
    queryset = ZipCode.objects.all()
