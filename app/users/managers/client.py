from django.contrib.auth import get_user_model
from django.db import models, transaction

from core.models import Phone

User = get_user_model()


class ClientManager(models.Manager):
    def create_client(self, email, password, number):
        with transaction.atomic():
            user = User.objects.create_user(email, password, is_active=True)

            client = self.create(user=user)
            phone = Phone.objects.create(client=client, number=number,)

            client.main_phone = phone
            client.save()

        return client
