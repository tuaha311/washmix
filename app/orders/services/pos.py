from orders.containers.order import OrderContainer
from orders.models import Order
from orders.services.order import OrderService
from users.models import Client, Employee


class POSService:
    def __init__(self, client: Client, order: Order, employee: Employee):
        self._client = client
        self._order = order
        self._employee = employee

    def checkout(self) -> OrderContainer:
        client = self._client
        order = self._order
        employee = self._employee

        order_service = OrderService(client)
        order_container = order_service.checkout(order)
        order_service.finalize(order, employee)

        return order_container
