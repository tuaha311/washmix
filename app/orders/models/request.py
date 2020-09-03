from core.common_models import Common


# TODO новые модели OrderItem (quantity), Cart
# TODO новые модели DeliveryInterval
class Request(Common):
    """
    Request to pickup order or drop off a order to the client.
    """

    class Meta:
        verbose_name = "pickup request"
        verbose_name_plural = "pickup requests"
