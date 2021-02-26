from django.conf import settings

from core.containers import BaseDynamicAmountContainer
from core.utils import get_dollars
from deliveries.containers.delivery import DeliveryContainer
from deliveries.models import Request
from orders.containers.basket import BasketContainer
from subscriptions.models import Subscription


class RequestContainer(BaseDynamicAmountContainer):
    """
    Wrapper container around pickup and dropoff Delivery.

    Delivery can be:
        - usual (default time)
        - rush (more faster order handling and delivery)

    Request has a complex pricing system - price is consists from
    3 different parts:
        - Auto-calculated usual delivery price based on client's subscription and basket.
        - Custom delivery price that can be set via POS by admin.
        - Rush delivery price that can be set via POS by admin.

    Request has only 1 discount (rush delivery doesn't have any discount):
        - discount = default delivery discount

    Total of request price can be calculated in 2 ways (different totals used in different cases):
        - amount_with_discount + rush_amount = total (price of default delivery with discount and rush price)
        - amount + rush_amount = price of default without discount and rush price

    It works in such manner because we faced with a lot of new business requirements.
    """

    proxy_to_object = "_request"

    def __init__(
        self,
        subscription: Subscription,
        request: Request,
        basket: BasketContainer,
    ):
        self._subscription = subscription
        self._request = request
        self._basket = basket

    @property
    def amount(self) -> int:
        """
        Default delivery price.
        This price doesn't depends from `is_rush` option.

        We have 2 cases here:
            - By default, this price is auto-calculated based on subscription.
            - Admin can provide custom delivery price in some cases and then this price will
            be used in calculation.
        """

        is_custom = self.is_custom
        calculated_amount = self.calculated_amount
        custom_amount = self.custom_amount
        amount = calculated_amount

        if is_custom:
            amount = custom_amount

        return amount

    @property
    def discount(self) -> int:
        """
        Default delivery discount.
        This discount doesn't depends from `is_rush` option.

        We have 2 cases here:
            - By default, this discount is auto-calculated based on subscription.
            - If admin privided custom delivery price, than discount will be equal to 0.
        """

        is_custom = self.is_custom
        discount = self.calculated_discount

        if is_custom:
            discount = settings.DEFAULT_ZERO_DISCOUNT

        return discount

    @property
    def calculated_amount(self) -> int:
        """
        This is the part of automatically calculated amount based on
        subscription and basket .
        """

        pickup_container = self.pickup_container
        dropoff_container = self.dropoff_container

        container_list = [pickup_container, dropoff_container]
        amount_list = [item.amount for item in container_list]

        calculated_amount = sum(amount_list)

        return calculated_amount

    @property
    def dollar_calculated_amount(self) -> float:
        return get_dollars(self, "calculated_amount")

    @property
    def calculated_discount(self) -> float:
        """
        This is the part of automatically calculated discount based on
        subscription and basket .
        """

        pickup_container = self.pickup_container
        dropoff_container = self.dropoff_container

        container_list = [pickup_container, dropoff_container]
        discount_list = [item.discount for item in container_list]

        calculated_discount = sum(discount_list)

        return calculated_discount

    @property
    def dollar_calculated_discount(self) -> float:
        return get_dollars(self, "calculated_discount")

    @property
    def custom_amount(self) -> int:
        """
        If Request has option `is_custom` enabled - than admin can provide
        custom delivery price.
        If option is disabled - then price will be equal to 0.
        """

        is_custom = self.is_custom
        original = self.original
        custom_amount = original.custom_amount

        if is_custom:
            return custom_amount
        return settings.DEFAULT_ZERO_AMOUNT

    @property
    def dollar_custom_amount(self) -> float:
        return get_dollars(self, "custom_amount")

    @property
    def rush_amount(self) -> int:
        """
        If Request has option `is_rush` enabled - than admin can provide
        custom rush delivery price.
        This amount doesn't depends from default delivery price.
        Rush delivery doesn't have any discounts.

        If option is disabled - then price will be equal to 0.
        """

        is_rush = self.is_rush
        original = self.original
        rush_amount = original.rush_amount

        if is_rush:
            return rush_amount
        return settings.DEFAULT_ZERO_AMOUNT

    @property
    def dollar_rush_amount(self) -> float:
        return get_dollars(self, "rush_amount")

    @property
    def total(self) -> float:
        amount_with_discount = self.amount_with_discount
        rush_amount = self.rush_amount

        total = amount_with_discount + rush_amount

        return total

    @property
    def dollar_total(self) -> float:
        return get_dollars(self, "total")

    @property
    def is_free(self) -> bool:
        total = self.total
        is_paid = bool(total)
        is_free = not is_paid

        return is_free

    @property
    def pickup_container(self) -> DeliveryContainer:
        subscription = self._subscription
        basket = self._basket
        pickup = self._request.pickup

        pickup_container = DeliveryContainer(subscription, pickup, basket)

        return pickup_container

    @property
    def dropoff_container(self) -> DeliveryContainer:
        subscription = self._subscription
        basket = self._basket
        dropoff = self._request.dropoff

        dropoff_container = DeliveryContainer(subscription, dropoff, basket)

        return dropoff_container
