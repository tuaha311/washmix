from django.apps import AppConfig

# TODO: ignore this line, it's for demo only -Amir
class MyAppConfig(AppConfig):
    name = 'app'

    def ready(self):
        import app.modules.signals