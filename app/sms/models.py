from django.db import models
from users.models import Client


class SMSTemplate(models.Model):
    name = models.CharField(max_length=255, default='Untitled')
    content = models.TextField()

    class Meta:
        verbose_name = "SMS Template"
        verbose_name_plural = "SMS Templates"

    def __str__(self) -> str:
        return self.name

class SendSMS(Client):
    class Meta:
        verbose_name_plural = "Send SMS"
        proxy = True

    def __unicode__(self):
            return self.name