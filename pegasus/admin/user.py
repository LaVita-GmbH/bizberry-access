from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin import register, StackedInline
from ..models import User, UserAccessToken


class UserAccessTokenInline(StackedInline):
    model = UserAccessToken
    fields = ('token', 'last_used', 'create_date', 'scopes',)
    readonly_fields = ('token', 'last_used', 'create_date',)
    filter_horizontal = ('scopes',)
    extra = 0


@register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('id', 'tenant', 'password')}),
        (_('Personal info'), {'fields': ('email',)}),
        (_('Permissions'), {
            'fields': ('status', 'is_superuser', 'role',),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('id',)

    list_display = ('id', 'tenant', 'email', 'is_active', 'role',)
    list_filter = ('is_superuser', 'status', 'tenant', 'groups', 'role')
    search_fields = ('email',)
    ordering = ('email',)

    inlines = [
        UserAccessTokenInline,
    ]
