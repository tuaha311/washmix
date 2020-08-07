from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from api.v1_0.serializers.customers import CustomerSerializer
from users.models import Customer


class CustomerCreateView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

    def perform_create(self, serializer):
        serializer.save(kind=Customer.INTERESTED)
