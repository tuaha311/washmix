from django.apps import AppConfig


class DeliveriesConfig(AppConfig):
    name = "deliveries"

    def ready(self):
        from deliveries import signals
