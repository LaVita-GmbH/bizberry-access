from django.contrib.admin import ModelAdmin, register
from ..models import Scope


@register(Scope)
class ScopeAdmin(ModelAdmin):
    fields = ('service', 'resource', 'action', 'selector',)
