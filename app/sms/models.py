from django.db import models

class SMSTemplate(models.Model):
    content = models.TextField()
    
    def __str__(self) -> str:
        return self.content[:50]
