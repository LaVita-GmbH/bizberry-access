from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin import register, StackedInline, TabularInline
from ..models import User, UserAccessToken, UserRoleRelation


class UserAccessTokenInline(StackedInline):
    model = UserAccessToken
    fields = ('token', 'last_used', 'create_date', 'scopes',)
    readonly_fields = ('token', 'last_used', 'create_date',)
    filter_horizontal = ('scopes',)
    extra = 0


class UserRoleRelationInline(TabularInline):
    model = UserRoleRelation
    fields = ('role', 'tenant',)
    extra = 0


@register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('id', 'password')}),
        (_('Personal info'), {'fields': ('email',)}),
        (_('Permissions'), {
            'fields': ('status', 'is_superuser',),
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
    filter_horizontal = ('roles',)

    list_display = ('id', 'email', 'is_active')
    list_filter = ('is_superuser', 'status', 'groups')
    search_fields = ('email',)
    ordering = ('email',)

    inlines = [
        UserAccessTokenInline,
        UserRoleRelationInline,
    ]
