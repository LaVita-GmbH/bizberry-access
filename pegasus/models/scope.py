from typing import List
from django.db import models
from django.db.models import indexes
from django.forms.models import model_to_dict
from django.utils.functional import cached_property
from djutils.crypt import random_string_generator


def _default_scope_id():
    return random_string_generator(size=32)


class Scope(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=_default_scope_id, editable=False)
    service = models.CharField(max_length=24, db_index=True)
    resource = models.CharField(max_length=24)
    action = models.CharField(max_length=48)
    selector = models.CharField(max_length=32, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @cached_property
    def keys(self) -> List[str]:
        return [value for _, value in model_to_dict(self, fields=('service', 'resource', 'action', 'selector')).items() if value]

    @cached_property
    def code(self) -> str:
        return '.'.join(self.keys)

    def __str__(self):
        return self.code

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('service', 'resource', 'action', 'selector',), name='scope_keys_unique'),
        ]

        indexes = [
            models.Index(fields=('service', 'resource', 'action',)),
            models.Index(fields=('service', 'resource', 'action', 'selector',)),
        ]
