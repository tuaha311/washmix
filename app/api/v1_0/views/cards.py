from rest_framework.viewsets import ModelViewSet

from api.v1_0.serializers.cards import CardSerializer


class CardViewSet(ModelViewSet):
    serializer_class = CardSerializer

    def perform_create(self, serializer: CardSerializer):
        client = self.request.user.client

        # helper = StripeHelper.create_payment_method()

        return serializer.save(client=client)

    def get_queryset(self):
        client = self.request.user.client

        return client.card_list.all()
