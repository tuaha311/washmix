from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from subscriptions.api.serializers.packages import PackageSerializer
from subscriptions.models import Package


class PackageListView(ListAPIView):
    """
    PUBLIC METHOD.

    Shows a list of available packages.
    Mostly called from landing without authentication.
    """

    permission_classes = [AllowAny]
    serializer_class = PackageSerializer
    queryset = Package.objects.all()
