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
    scopes = models.ManyToManyField(Scope, related_name='roles', blank=True)
    is_default_role = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.name} ({self.id})'

    async def get_scopes(self, exclude_roles: Optional[set] = set()) -> Set[Scope]:
        scopes = set()
        exclude_roles.add(self.id)

        @sync_to_async
        def get_scopes():
            return list(self.scopes.filter(is_active=True))

        scopes.update(await get_scopes())

        @sync_to_async
        def get_roles():
            return list(self.included_roles.exclude(id__in=exclude_roles))

        for role in await get_roles():
            scopes.update(await role.get_scopes(exclude_roles=exclude_roles))

        return scopes

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('is_default_role',), name='is_default_role_unique', condition=models.Q(is_default_role=True)),
        ]
