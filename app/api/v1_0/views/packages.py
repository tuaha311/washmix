from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1_0.serializers.packages import PackageSerializer, SetPackageSerializer
from core.models import Package
from core.package_handler import PackageHandler


class PackageListView(ListAPIView):
    """
    PUBLIC METHOD.

    Shows a list of available packages.
    Mostly called from landing without authentication.
    """

    permission_classes = [AllowAny]
    serializer_class = PackageSerializer
    queryset = Package.objects.all()


class SetPackageView(GenericAPIView):
    serializer_class = SetPackageSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        client = request.user.client

        handler = PackageHandler(client)
        new_package = handler.change(serializer.validated_data["package"])

        return Response({"package": new_package.name})
