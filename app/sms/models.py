from django.db import models

class SMSTemplate(models.Model):
    content = models.TextField()

    class Meta:
        verbose_name = "Send SMS"
        verbose_name_plural = "Send SMS"

    def __str__(self) -> str:
        return self.content[:50]