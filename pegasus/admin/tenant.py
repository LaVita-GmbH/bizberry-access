from django.contrib.admin import ModelAdmin, register
from ..models import Tenant


@register(Tenant)
class TenantAdmin(ModelAdmin):
    fields = ('id', 'name',)
    readonly_fields = ('id',)

    list_display = ('id', 'name',)
