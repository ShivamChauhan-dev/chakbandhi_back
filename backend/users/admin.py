from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from drone_destination.base_admin import CreatorAdminMixin
from .models import FCMTokens, DDUser, OTPLog


@admin.register(DDUser)
class DDUserAdmin(UserAdmin):
    list_display = ('username', 'is_staff', 'group')
    search_fields = ['username', 'email']

    def group(self, obj):
        return '\n'.join([f'{group}' for group in obj.groups.all()])


@admin.register(OTPLog)
class OTPLogAdmin(CreatorAdminMixin):
    list_display = ('code', 'token', 'is_utilized')


@admin.register(FCMTokens)
class FCMTokensAdmin(CreatorAdminMixin):
    list_display = ('token', 'device')

