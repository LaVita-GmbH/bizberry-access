from django.contrib.admin import ModelAdmin, register, TabularInline
from ..models import Tenant, TenantCountry


class TenantCountryInline(TabularInline):
    model = TenantCountry
    fields = ('code',)
    extra = 0


@register(Tenant)
class TenantAdmin(ModelAdmin):
    fields = ('id', 'name',)
    readonly_fields = ('id',)

    list_display = ('id', 'name',)

    inlines = [
        TenantCountryInline,
    ]
