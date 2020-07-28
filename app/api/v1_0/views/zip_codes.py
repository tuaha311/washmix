from rest_framework.viewsets import ModelViewSet

from api.v1_0.serializers.zip_codes import ZipCodeSerializer
from core.models import ZipCode


class ZipCodeViewSet(ModelViewSet):
    """
    Methods to manipulate with `ZipCode` entity
    """

    serializer_class = ZipCodeSerializer
    queryset = ZipCode
