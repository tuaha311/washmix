from rest_framework.generics import ListAPIView

from api.v1_0.serializers.packages import PackageSerializer
from core.models import Package


class PackageListView(ListAPIView):
    serializer_class = PackageSerializer
    queryset = Package.objects.all()
