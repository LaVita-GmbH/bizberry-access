from typing import List

from django.db import models
from django.utils.functional import cached_property
from djutils.crypt import random_string_generator


def _default_scope_id():
    return random_string_generator(size=32)


class Scope(models.Model):
    id = models.CharField(
        max_length=32, primary_key=True, default=_default_scope_id, editable=False
    )
    service: str = models.CharField(max_length=24, db_index=True)
    resource: str = models.CharField(max_length=24)
    action: str = models.CharField(max_length=48)
    selector: str = models.CharField(max_length=32, null=True, blank=True)
    is_active: bool = models.BooleanField(default=True)
    is_internal: bool = models.BooleanField(default=False)
    is_critical: bool = models.BooleanField(default=False)

    @cached_property
    def keys(self) -> List[str]:
        return list(
            filter(
                lambda s: s,
                [
                    self.service,
                    self.resource,
                    self.action,
                    self.selector,
                ],
            )
        )

    @cached_property
    def code(self) -> str:
        return ".".join(self.keys)

    def __str__(self):
        return self.code

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "service",
                    "resource",
                    "action",
                    "selector",
                ),
                name="scope_keys_unique",
            ),
        ]

        indexes = [
            models.Index(
                fields=(
                    "service",
                    "resource",
                    "action",
                )
            ),
            models.Index(
                fields=(
                    "service",
                    "resource",
                    "action",
                    "selector",
                )
            ),
        ]
