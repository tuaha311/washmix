from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class SMSTemplate(models.Model):
    content = models.TextField()

    def __str__(self):
        return f"Template {self.pk}"
