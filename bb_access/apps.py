from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'bb_access'

    def ready(self) -> None:
        from .events import publish
