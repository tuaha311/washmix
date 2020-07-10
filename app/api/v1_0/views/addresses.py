from rest_framework.viewsets import ModelViewSet

from api.v1_0.serializers.addresses import AddressSerializer


class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer

    def get_queryset(self):
        return self.request.user.address_list.all()
