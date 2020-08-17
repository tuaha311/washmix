from rest_framework.viewsets import ModelViewSet

from api.v1_0.serializers.phones import PhoneSerializer


class PhoneViewSet(ModelViewSet):
    """
    Methods to manipulate with `Address` entity
    """

    serializer_class = PhoneSerializer

    def get_queryset(self):
        return self.request.user.client.phone_list.all()
