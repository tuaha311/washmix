from django.conf import settings

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.client.mixins import SetMainAttributeMixin
from billing.api.serializers.cards import CardSerializer
from billing.services.card import CardService
from notifications.tasks import send_email


class CardViewSet(SetMainAttributeMixin, ModelViewSet):
    serializer_class = CardSerializer
    main_attribute = "main_card"
    removed_text = "removed from"
    updated_text = "updated from"

    def get_queryset(self):
        client = self.request.user.client
        return client.card_list.all()

    def perform_destroy(self, instance):
        client = self.request.user.client
        client_id = client.id
        stripe_id = instance.stripe_id
        recipient_list = [client.email]

        # in super class we have validation on
        # removing main card - and we are running it first
        super().perform_destroy(instance)

        # if card was removed from DB, we can remove it
        # from Stripe account
        service = CardService(client)
        service.remove_card(stripe_id)

        send_email.send(
            event=settings.CARD_CHANGES,
            recipient_list=recipient_list,
            extra_context={
                "client_id": client_id,
                "action": self.updated_text,
            },
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        client = request.user.client
        card_list_length = len(client.card_list.all())

        if card_list_length == 1:
            try:
                latest_card = client.card_list.latest("id")  # Fetch the latest added card
                client.main_card = latest_card
                client.save()
            except:
                pass

            message = f"Dear {client.full_name} as part of WashMix, we require all account holders to have a Valid Credit Card on file as their default payment method - In order to delete this card, you can first add a New Card, and then remove this card."
            return Response({"message": message}, status=status.HTTP_412_PRECONDITION_FAILED)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CardRefreshView(GenericAPIView):
    response_serializer_class = CardSerializer

    def post(self, request: Request, *args, **kwargs):
        client = self.request.user.client
        card_service = CardService(client)
        card_list = card_service.save_card_list()

        response = self.response_serializer_class(card_list, many=True).data

        try:
            latest_card = client.card_list.latest("id")  # Fetch the latest added card
            if client.main_card != latest_card:
                client.main_card = latest_card
                client.save()

        except Exception as e:
            print("Something went wrong, could not update the main card.")
            print(f"Exception message: {str(e)}")

        return Response(response)
