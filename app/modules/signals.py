from django.contrib.auth.hashers import identify_hasher
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from utilities.wm_email_config import WMEmailControllerSendGrid, wm_user_confirmation_email


def user_register_email(sender, instance, created=None, *args, **kwargs):
    if created:
        # This is to check if user comes in from a Social Website.
        try:
            identify_hasher(instance.password)
        except:
            return

        try:
            WMEmailControllerSendGrid(
                email_formatter=wm_user_confirmation_email(user=instance)
            ).send_sendgrid_email()
        except:
            pass


post_save.connect(user_register_email, sender=User)
