from django.core.management.base import BaseCommand, CommandParser

from bb_access.events.subscribe import consumer


class Command(BaseCommand):
    help = "Sync scopes and roles in database with defined scopes and roles in yml file"

    def add_arguments(self, parser: CommandParser):
        pass

    def handle(self, *args, **options):
        consumer.run()
