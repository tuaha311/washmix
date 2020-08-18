from rest_framework.viewsets import ModelViewSet

from api.v1_0.serializers.addresses import AddressSerializer


class AddressViewSet(ModelViewSet):
    """
    Methods to manipulate with `Address` entity
    """

    serializer_class = AddressSerializer

    def get_queryset(self):
        return self.request.user.client.address_list.all()

    def perform_create(self, serializer):
        return serializer.save(client=self.request.user.client)
