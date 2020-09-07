from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from users.models import Customer
from users.serializers.customers import CustomerSerializer


class CustomerCreateView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

    def perform_create(self, serializer):
        serializer.save(kind=Customer.INTERESTED)
