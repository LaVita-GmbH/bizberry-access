import os.path
import yaml
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.conf import settings
from ...models import Scope


class Command(BaseCommand):
    help = 'Sync Scopes in database with defined scopes in yml file'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('--file', type=str, default=os.path.join(settings.BASE_DIR, 'scopes.yml'), required=False)

    def handle(self, *args, **options):
        current_scopes = []

        with open(options['file'], 'r') as file:
            definition = yaml.load(file, Loader=yaml.Loader)
            services = definition['scopes']['services']
            for service in services:
                for resource in service['resources']:
                    if resource.get('internal'):
                        continue

                    for action in resource['actions']:
                        if action.get('internal'):
                            continue

                        selectors = action.get('selectors') or [{'key': None}]
                        for selector in selectors:
                            if selector.get('internal'):
                                continue

                            print(service['key'], resource['key'], action['key'], selector['key'])
                            scope, _ = Scope.objects.get_or_create(
                                service=service['key'],
                                resource=resource['key'],
                                action=action['key'],
                                selector=selector['key'],
                            )

                            if not scope.is_active:
                                scope.is_active = True
                                scope.save()

                            current_scopes.append(scope)

        old_scopes = Scope.objects.exclude(id__in=[scope.id for scope in current_scopes])
        old_scopes.update(is_active=False)
