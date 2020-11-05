from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from users.api.serializers.customers import CustomerSerializer
from users.models import Customer


class CustomerCreateView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
