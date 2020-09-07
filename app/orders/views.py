from rest_framework.viewsets import ModelViewSet

from orders.serializers import OrderSerializer


class OrderViewSet(ModelViewSet):
    """
    Methods to manipulate with `Order` entity
    """

    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.request.user.order_list.all()
