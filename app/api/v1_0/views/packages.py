from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from api.v1_0.serializers.packages import PackageSerializer
from core.models import Package


class PackageListView(ListAPIView):
    """
    PUBLIC METHOD.

    Shows a list of available packages.
    Mostly called from landing without authentication.
    """

    permission_classes = [AllowAny]
    serializer_class = PackageSerializer
    queryset = Package.objects.all()
