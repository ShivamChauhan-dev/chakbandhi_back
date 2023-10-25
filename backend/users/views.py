from django.http import HttpResponse
from drone_destination.mixins import CreatorAPIViewMixin, StaffEditorPermissionMixin, UserQuerySetMixin
from drone_destination.pagination import StandardResultSetPagination
from rest_framework import filters, generics, status
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import *
from .serializers import (
    FCMTokenSerializer, GenerateOTPSerializer, DDUserUpdateInlineSerializer,
    DDUserInlineSerializer, OTPLoginSerializer
)


class OTPSendView(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    queryset = OTPLog.objects.all()
    serializer_class = GenerateOTPSerializer


class ValidateOTPView(TokenObtainPairView):
    queryset = OTPLog.objects.all()
    serializer_class = OTPLoginSerializer


class UsersListAPIView(UserQuerySetMixin, StaffEditorPermissionMixin, generics.ListAPIView):
    serializer_class = DDUserInlineSerializer
    queryset = DDUser.objects.all()
    pagination_class = StandardResultSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name']
    ordering_fields = ['username', 'first_name', 'last_name']


class UserUpdateAPIView(UserQuerySetMixin, StaffEditorPermissionMixin, generics.RetrieveUpdateAPIView):
    serializer_class = DDUserUpdateInlineSerializer
    queryset = DDUser.objects.all()
    lookup_field = 'username'


class FCMTokenView(CreatorAPIViewMixin, generics.CreateAPIView):
    queryset = FCMTokens.objects.all()
    serializer_class = FCMTokenSerializer
    permission_classes = ()

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        # return Response(status=status.HTTP_204_NO_CONTENT)
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
