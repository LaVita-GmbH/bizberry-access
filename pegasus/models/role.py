from typing import Optional, Set
from asgiref.sync import sync_to_async, async_to_sync
from django.db import models
from django.db.models import constraints
from djutils.crypt import random_string_generator
from . import Scope


def _default_group_id():
    return random_string_generator(size=32)


class Role(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=_default_group_id, editable=False)
    name = models.CharField(max_length=56)
    included_roles = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='+')
    scopes = models.ManyToManyField(Scope, related_name='roles', blank=True, limit_choices_to={'is_active': True, 'is_internal': False})
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.name} ({self.id})'

    async def get_scopes(self, include_critical: bool = True, exclude_roles: Optional[set] = None) -> Set[Scope]:
        scopes = set()
        if not exclude_roles:
            exclude_roles = set()

        exclude_roles.add(self.id)

        @sync_to_async
        def get_scopes():
            filters = models.Q(is_active=True, is_internal=False)
            if not include_critical:
                filters &= models.Q(is_critical=False)

            return list(self.scopes.filter(filters))

        scopes.update(await get_scopes())

        @sync_to_async
        def get_roles():
            return list(self.included_roles.exclude(id__in=exclude_roles))

        for role in await get_roles():
            scopes.update(await role.get_scopes(exclude_roles=exclude_roles))

        return scopes

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('is_default',), name='is_default_unique', condition=models.Q(is_default=True)),
        ]
