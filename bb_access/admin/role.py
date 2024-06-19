from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.admin import ModelAdmin, register

from bb_access.models import Role


@register(Role)
class RoleAdmin(ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": ("name",),
            },
        ),
        (
            _("Scopes"),
            {
                "fields": (
                    "scopes",
                    "included_roles",
                ),
            },
        ),
        (
            _("Options"),
            {
                "fields": ("is_default",),
            },
        ),
    ]

    filter_horizontal = (
        "scopes",
        "included_roles",
    )

    list_display = (
        "id",
        "name",
        "is_default",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
