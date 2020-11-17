import os.path
import logging
from typing import Any, List
import yaml
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.conf import settings
from ...models import Scope, Role


_logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync scopes and roles in database with defined scopes and roles in yml file'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('--file', type=str, default=os.path.join(settings.BASE_DIR, 'access.yml'), required=False)

    @classmethod
    def _get_attribute_with_fallbacks(cls, key: str, objects: List[dict], fallback: Any = None):
        for obj in objects:
            try:
                return obj[key]

            except KeyError:
                pass

        return fallback

    def sync_scopes(self, scopes):
        services = scopes['services']
        current_scopes = []

        for service in services:
            for resource in service['resources']:
                for action in resource['actions']:
                    selectors = action.get('selectors') or [{'key': None}]
                    for selector in selectors:
                        scope, _ = Scope.objects.get_or_create(
                            service=service['key'],
                            resource=resource['key'],
                            action=action['key'],
                            selector=selector['key'],
                        )
                        _logger.info("Apply Scope %s", scope)

                        scope.is_active = True
                        scope.is_internal = self._get_attribute_with_fallbacks('internal', [selector, action, resource, service], False)
                        scope.is_critical = self._get_attribute_with_fallbacks('critical', [selector, action, resource, service], False)

                        scope.save()
                        current_scopes.append(scope)

        old_scopes = Scope.objects.exclude(id__in=[scope.id for scope in current_scopes])
        old_scopes.update(is_active=False)
        if old_scopes:
            _logger.info("Deactivated %i scopes", len(old_scopes))

    def sync_roles(self, roles):
        current_roles = []
        for role in roles:
            _logger.info("Apply role %s", role.get('key'))
            role_obj, _ = Role.objects.get_or_create(name=role.get('key'))

            role_obj.is_active = True
            role_obj.is_default = role.get('is_default', False)

            scope_objs = []
            for scope in role.get('scopes', []):
                service, resource, action, selector = (scope.get('code').split('.') + [None])[:4]
                scope_obj = Scope.objects.get(service=service, resource=resource, action=action, selector=selector)
                _logger.info("Apply Scope %s to Role %s", scope_obj, role_obj)
                scope_objs.append(scope_obj)

            role_obj.scopes.set(scope_objs)

            included_role_objs = []
            for included_role in role.get('included_roles', []):
                included_role_objs.append(Role.objects.get(name=included_role.get('key')))

            role_obj.included_roles.set(included_role_objs)

            role_obj.save()
            current_roles.append(role_obj)

        old_roles = Role.objects.exclude(id__in=[role.id for role in current_roles])
        old_roles.update(is_active=False)
        if old_roles:
            _logger.info("Deactivated %i roles", len(old_roles))

    def handle(self, *args, **options):
        with open(options['file'], 'r') as file:
            definition = yaml.load(file, Loader=yaml.Loader)
            self.sync_scopes(definition['scopes'])
            self.sync_roles(definition['roles'])
