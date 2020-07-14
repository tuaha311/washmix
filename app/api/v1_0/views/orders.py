from rest_framework.viewsets import ModelViewSet

from api.v1_0.serializers.orders import OrderSerializer


class OrderViewSet(ModelViewSet):
    """
    Methods to manipulate with `Order` entity
    """

    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.request.user.order_list.all()
