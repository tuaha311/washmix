from dataclasses import dataclass


@dataclass
class PaymentContainer:
    """
    This container implements same interface like stripe.PaymentMethod.
    """

    id: str
    amount: int
