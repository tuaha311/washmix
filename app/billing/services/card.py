from typing import List, Optional

from billing.models import Card
from billing.stripe_helper import StripeHelper
from users.models import Client


class CardService:
    """
    Main purpose of this service is to save user's card list in WashMix
    for later billing.

    Capabilities:
        - Save user's card list in WashMix
        - Update main card
    """

    def __init__(self, client: Client):
        self._client = client
        self._stripe_helper = StripeHelper(client)

    def save_card_list(self) -> Optional[List[Card]]:
        """
        Save card list for user.
        """

        # we are saving all cards received from Stripe
        # in most cases it is only 1 card.
        payment_method_list = self._stripe_helper.payment_method_list

        for item in payment_method_list:
            card, _ = Card.objects.get_or_create(
                client=self._client,
                stripe_id=item.id,
                defaults={
                    "last": item.card.last4,
                    "expiration_month": item.card.exp_month,
                    "expiration_year": item.card.exp_year,
                },
            )

        return self._client.card_list.all()

    @classmethod
    def update_main_card(cls, client: Client, card: Card):
        client.main_card = card
        client.save()

        return card
