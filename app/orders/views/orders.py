from rest_framework.viewsets import ModelViewSet

from orders.serializers.orders import OrderSerializer


class OrderViewSet(ModelViewSet):
    """
    Methods to manipulate with `Order` entity
    """

    serializer_class = OrderSerializer

    def get_queryset(self):
        client = self.request.user.client
        return client.order_list.all()
