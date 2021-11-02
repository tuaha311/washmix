from django.db import models

from deliveries.models import Delivery, Request


class ArchivedRequest(Request):
    class Meta:
        proxy = True
        verbose_name = "Request"
        verbose_name_plural = "Requests"
        ordering = ["-created"]


class ArchivedDelivery(Delivery):
    class Meta:
        proxy = True
        verbose_name = "Delivery"
        verbose_name_plural = "Deliveries"
        ordering = ["-date", "sorting", ]
