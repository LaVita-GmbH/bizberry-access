from typing import Optional, Set
from django.db import models
from djutils.crypt import random_string_generator
from . import Scope


def _default_group_id():
    return random_string_generator(size=32)


class Role(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=_default_group_id, editable=False)
    name = models.CharField(max_length=56)
    included_roles = models.ManyToManyField('self', blank=True)
    scopes = models.ManyToManyField(Scope, related_name='roles', blank=True)

    def __str__(self) -> str:
        return f'{self.name} ({self.id})'

    def get_scopes(self, exclude_roles: Optional[set] = set()) -> Set[Scope]:
        scopes = set()
        exclude_roles.add(self.id)
        for role in self.included_roles.exclude(id__in=exclude_roles):
            scopes.update(role.get_scopes(exclude_roles=exclude_roles))

        scopes.update([scope for scope in self.scopes.all()])

        return scopes
