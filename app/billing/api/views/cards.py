from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.client.mixins import PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin
from billing.api.serializers.cards import CardSerializer
from billing.services.card import CardService


class CardViewSet(PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin, ModelViewSet):
    # TODO remove PATCH / PUT methods

    serializer_class = CardSerializer
    main_attribute = "main_card"

    def get_queryset(self):
        client = self.request.user.client
        return client.card_list.all()


class CardRefreshView(GenericAPIView):
    response_serializer_class = CardSerializer

    def post(self, request: Request, *args, **kwargs):
        client = self.request.user.client

        card_service = CardService(client)
        card_list = card_service.save_card_list()

        response = self.response_serializer_class(card_list, many=True).data

        return Response(response)
