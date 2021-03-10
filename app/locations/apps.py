from django.apps import AppConfig


class LocationsConfig(AppConfig):
    name = "locations"

    def ready(self):
        from locations import signals
