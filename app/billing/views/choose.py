from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from billing.serializers.choose import ChooseResponseSerializer, ChooseSerializer
from billing.services.choose import ChooseService


class ChooseView(GenericAPIView):
    serializer_class = ChooseSerializer
    response_serializer_class = ChooseResponseSerializer

    def post(self, request: Request, *args, **kwargs):
        package_serializer = self.serializer_class(data=request.data, context={"request": request})
        package_serializer.is_valid(raise_exception=True)

        client = request.user.client
        package = package_serializer.validated_data["package"]

        handler = ChooseService(client)
        invoice = handler.choose(package)

        response = self.response_serializer_class(invoice).data

        return Response(response)
