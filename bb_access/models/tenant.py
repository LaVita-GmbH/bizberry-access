from django.db import models
from djutils.crypt import random_string_generator
from djutils.models import ModelAtomicSave


def _default_tenant_id():
    return random_string_generator(size=16)


def _default_tenant_country_id():
    return random_string_generator(size=24)


class Tenant(ModelAtomicSave):
    id = models.CharField(
        max_length=16, primary_key=True, default=_default_tenant_id, editable=False
    )
    name: str = models.CharField(max_length=48, null=True, blank=True)


class TenantCountry(ModelAtomicSave):
    id = models.CharField(
        max_length=24,
        primary_key=True,
        default=_default_tenant_country_id,
        editable=False,
    )
    tenant: Tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="countries"
    )
    code: str = models.CharField(
        max_length=2, help_text="ISO 3166 Alpha-2 Country Code"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "tenant",
                    "code",
                ),
                name="tenant_code_unique",
            ),
        ]
