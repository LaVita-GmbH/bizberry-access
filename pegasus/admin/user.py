from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin import register, StackedInline
from ..models import User, UserAccessToken


class UserAccessTokenInline(StackedInline):
    model = UserAccessToken
    fields = ('token', 'last_used', 'create_date', 'scopes',)
    readonly_fields = ('token', 'last_used', 'create_date',)
    extra = 0


@register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('id', 'password')}),
        (_('Personal info'), {'fields': ('email',)}),
        (_('Permissions'), {
            'fields': ('status', 'is_superuser',),
        }),
        (_('Scopes'), {
            'fields': ('roles', 'scopes',),
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
    filter_horizontal = ('roles', 'scopes',)

    list_display = ('id', 'email', 'is_active')
    list_filter = ('is_superuser', 'status', 'groups')
    search_fields = ('email',)
    ordering = ('email',)

    inlines = [
        UserAccessTokenInline,
    ]
