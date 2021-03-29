from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from notifications.tasks import send_email

User = get_user_model()


def remove_user_relation_with_all_info(queryset: QuerySet, filter_query: dict):
    """
    Helper method that performs deletion of User's model with it relations.
    Also it will notify a removed email about deletion.
    """

    item_list = [{"email": item.email, "full_name": item.full_name} for item in queryset]

    user_queryset = User.objects.filter(**filter_query)

    user_queryset.delete()
    queryset.delete()

    for item in item_list:
        email = item["email"]
        full_name = item["full_name"]
        recipient_list = [email]

        send_email.send(
            event=settings.ACCOUNT_REMOVED,
            recipient_list=recipient_list,
            extra_context={
                "full_name": full_name,
            },
        )
