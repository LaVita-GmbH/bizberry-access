from django.apps import AppConfig


class bb_accessAppConfig(AppConfig):
    name = 'bb_access'

    def ready(self) -> None:
        from .events import publish
