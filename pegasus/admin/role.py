from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.admin import ModelAdmin, register
from ..models import Role


@register(Role)
class RoleAdmin(ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ('name',),
        }),
        (_('Scopes'), {
            'fields': ('scopes', 'included_roles',),
        }),
        (_('Options'), {
            'fields': ('default_role',),
        }),
    ]

    filter_horizontal = ('scopes', 'included_roles',)

    list_display = ('id', 'name', 'default_role',)
