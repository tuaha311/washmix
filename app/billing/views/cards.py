from rest_framework.viewsets import ModelViewSet

from api.v1_0.mixins import PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin
from billing.serializers.cards import CardSerializer


class CardViewSet(PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin, ModelViewSet):
    # TODO remove PATCH / PUT methods

    serializer_class = CardSerializer
    main_attribute = "main_card"

    def get_queryset(self):
        client = self.request.user.client
        return client.card_list.all()
