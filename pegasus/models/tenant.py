from django.db import models
from djutils.crypt import random_string_generator


def _default_tenant_id():
    return random_string_generator(size=16)


class Tenant(models.Model):
    id = models.CharField(max_length=16, primary_key=True, default=_default_tenant_id, editable=False)
    name = models.CharField(max_length=48, null=True, blank=True)
