from django.contrib import admin
from accounts.forms import UserCreationForm, UserChangeForm
from accounts.models import User, OtpCode
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('phone_number', 'email', 'is_staff', 'created_at_jalali')
    list_filter = ('is_staff',)
    fieldsets = (
        (
            None,
            {'fields': ('phone_number', 'email', 'first_name', 'last_name', 'state', 'city', 'address', 'zip_code',
                        'password')},
        ),
        (
            'Permissions',
            {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'last_login',)}
        )
    )
    add_fieldsets = (
        (
            None,
            {'fields': ('phone_number', 'email', 'first_name', 'last_name', 'state', 'city', 'address', 'zip_code',
                        'password1', 'password2')},
        ),
    )
    search_fields = ('phone_number', 'email')
    ordering = ('-created_at',)
    readonly_fields = ('last_login',)
    filter_horizontal = ('groups', 'user_permissions',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:  # checks if user is superuser...
            form.base_fields['is_superuser'].disabled = True  # it doesn't show is_superuser field in admin panel
        if not request.user.is_staff:  # checks if user is staff...
            form.base_fields['is_staff'].disabled = True  # it doesn't show is_staff field in admin panel

        return form


@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'created_at', 'created_at_jalali')


admin.site.unregister(Group)
