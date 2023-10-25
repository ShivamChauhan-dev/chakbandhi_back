from django.db.models.query import QuerySet
from rest_framework import permissions, serializers
from rest_framework.request import Request

from users.models import DDUser
from users.serializers import DDUserInlineSerializer
from .permissions import IsStaffEditorPermission


class StaffEditorPermissionMixin:
    permission_classes = [permissions.IsAdminUser, IsStaffEditorPermission]


def build_lookup(request: Request, user_field_name, filter_user=None):
    user: DDUser = request.user

    if str(user.id) == str(filter_user):
        return {user_field_name: filter_user}
    elif user.has_full_access() or user.is_superuser:
        return {}
    return {user_field_name: user.pk}


class OwnerQuerySetMixin:
    user_field = 'owner'
    allow_staff_view = False

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return self.valid_queryset(qs)

    def valid_queryset(self, queryset: QuerySet):
        request: Request = self.request
        lookup_data = build_lookup(request, self.user_field, request.query_params.get('creator'))
        return queryset.filter(**lookup_data)


class CreatorQuerySetMixin(OwnerQuerySetMixin):
    user_field = 'creator'


class CreatorRetrieveQuerySetMixin(OwnerQuerySetMixin):
    user_field = 'creator'

    def valid_queryset(self, queryset: QuerySet):
        user = self.request.user
        return super().valid_queryset(queryset).filter(**{self.user_field: user.pk})


class UserQuerySetMixin(OwnerQuerySetMixin):
    user_field = 'id'


class CreatorAPIViewMixin:

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class CreatorSerializerMixin(serializers.ModelSerializer):
    creator = DDUserInlineSerializer(read_only=True)
