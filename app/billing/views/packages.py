from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from billing.models import Package
from billing.serializers.packages import PackageSerializer


class PackageListView(ListAPIView):
    """
    PUBLIC METHOD.

    Shows a list of available packages.
    Mostly called from landing without authentication.
    """

    permission_classes = [AllowAny]
    serializer_class = PackageSerializer
    queryset = Package.objects.all()
