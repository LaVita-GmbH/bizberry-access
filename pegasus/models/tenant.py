from typing import List
from django.db import models
from django.db.models import constraints
from asgiref.sync import sync_to_async
from djutils.crypt import random_string_generator


def _default_tenant_id():
    return random_string_generator(size=16)


class Tenant(models.Model):
    id = models.CharField(max_length=16, primary_key=True, default=_default_tenant_id, editable=False)
    name = models.CharField(max_length=48, null=True, blank=True)

    @sync_to_async
    def get_countries(self) -> List['TenantCountry']:
        return list(self.countries.all())


class TenantCountry(models.Model):
    id = models.CharField(max_length=16, primary_key=True, default=_default_tenant_id, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='countries')
    code = models.CharField(max_length=2, help_text="ISO 3166 Alpha-2 Country Code")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('tenant', 'code',), name='tenant_code_unique'),
        ]
