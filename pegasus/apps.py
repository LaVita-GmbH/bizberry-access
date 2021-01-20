from django.apps import AppConfig


class PegasusAppConfig(AppConfig):
    name = 'pegasus'

    def ready(self) -> None:
        from .events import publish
