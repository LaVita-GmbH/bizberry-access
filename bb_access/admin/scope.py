from django.contrib.admin import ModelAdmin, register

from bb_access.models import Scope


@register(Scope)
class ScopeAdmin(ModelAdmin):
    fields = (
        "service",
        "resource",
        "action",
        "selector",
        "is_active",
    )
    list_display = fields
    list_display_links = fields[0:4]
    list_filter = (
        "is_active",
        "service",
        "resource",
    )

    ordering = fields

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
