from typing import List, Optional, Set

from django.db import models
from djutils.crypt import random_string_generator

from . import Scope


def _default_group_id():
    return random_string_generator(size=32)


class Role(models.Model):
    id = models.CharField(
        max_length=32, primary_key=True, default=_default_group_id, editable=False
    )
    name: str = models.CharField(max_length=56)
    included_roles = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="+"
    )
    scopes = models.ManyToManyField(
        Scope,
        related_name="roles",
        blank=True,
        limit_choices_to={"is_active": True, "is_internal": False},
    )
    is_default: bool = models.BooleanField(default=False)
    is_active: bool = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"

    def get_scopes(
        self, include_critical: bool = True, exclude_roles: Optional[set] = None
    ) -> Set[Scope]:
        scopes = set()
        if not exclude_roles:
            exclude_roles = set()

        exclude_roles.add(self.id)

        def get_scopes():
            filters = models.Q(is_active=True, is_internal=False)
            if not include_critical:
                filters &= models.Q(is_critical=False)

            return list(self.scopes.filter(filters))

        scopes.update(get_scopes())

        def get_roles():
            return list(self.included_roles.exclude(id__in=exclude_roles))

        for role in get_roles():
            scopes.update(
                role.get_scopes(
                    include_critical=include_critical, exclude_roles=exclude_roles
                )
            )

        return scopes

    def get_included_roles(self) -> List["Role"]:
        return list(self.included_roles.all())

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("is_default",),
                name="is_default_unique",
                condition=models.Q(is_default=True),
            ),
        ]
