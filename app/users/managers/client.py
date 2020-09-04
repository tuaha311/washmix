from django.contrib.auth import get_user_model
from django.db import IntegrityError, models, transaction

from core.models import Phone

User = get_user_model()


class ClientManager(models.Manager):
    def create_client(
        self, email: str, password: str, number: str, stripe_id: str = "", **extra_kwargs
    ):
        # when we have multiple workers, we can face with
        # situation when 2 simultaneous requests came to 2 different
        # gunicorn workers and pass validation checks and trying to
        # write records into database
        try:
            with transaction.atomic():
                user = User.objects.create_user(email, password, is_active=True, **extra_kwargs)

                client = self.create(user=user, stripe_id=stripe_id)
                phone = Phone.objects.create(client=client, number=number,)

                client.main_phone = phone
                client.save()
        except IntegrityError:
            user = User.objects.get(email=email)
            client = user.client

        return client
