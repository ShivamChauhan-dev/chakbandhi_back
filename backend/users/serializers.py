import uuid

from django.conf import settings
from django.contrib.auth.models import ContentType, Group, Permission
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from drone_destination.otp_sender import OTPSender
from .models import FCMTokens, DDUser, OTPLog, OTPSourceTypes


class ContentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContentType
        fields = "__all__"


class PermissionSerializer(serializers.ModelSerializer):
    content_type = ContentTypeSerializer(read_only=True)

    class Meta:
        model = Permission
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = "__all__"


class DDUserInlineSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = DDUser
        # fields = "__all__"
        fields = ["username", "id", "first_name", "last_name", "avatar"]
        read_only = ["username", "id", "first_name", "last_name", "avatar"]

    def get_avatar(self, obj: DDUser):
        return None

    def to_representation(self, instance):
        if type(instance) is list and type(instance[0]) is int:
            return DDUserInlineSerializer(DDUser.objects.filter(id__in=instance), many=True).data
        elif type(instance) is int:
            return DDUserInlineSerializer(DDUser.objects.get(pk=instance)).data

        return super().to_representation(instance)


class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = DDUserInlineSerializer(self.user).data
        return data


class GenerateOTPSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = OTPLog
        fields = ['mobile', 'token']
        read_only_fields = ['token']

    def validate_mobile(self, value):
        try:
            self.user_profile = DDUser.objects.get(mobile=value)
        except DDUser.DoesNotExist:
            raise ValidationError(f"User with {value} phone not found")

    def validate(self, attrs: dict):
        super().validate(attrs)
        provider: OTPSender = import_string(settings.OTP_PROVIDER_CLASS)(self.user_profile.mobile)
        provider.make_opt_request()
        return {
            "code": provider.opt_code,
            "creator": self.user_profile.creator,
            "sent_on": OTPSourceTypes.Phone,
            "token": uuid.uuid4()
        }


class JWTResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)
    user = DDUserInlineSerializer(read_only=True)
    token_class = RefreshToken

    @classmethod
    def get_token(cls, user):
        return cls.token_class.for_user(user)

    def build_data(self, user: DDUser):
        refresh = self.get_token(user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            'user': DDUserInlineSerializer(user).data
        }

        return data


class OTPLoginSerializer(JWTResponseSerializer):
    code = serializers.IntegerField(min_value=1000, max_value=9999, write_only=True)
    token = serializers.UUIDField(write_only=True)

    default_error_messages = {"no_active_account": _("OTP Validation Failed")}

    def validate(self, attrs):
        token = attrs['token']
        code = attrs['code']
        try:
            log: OTPLog = OTPLog.objects.get(code=code, token=token, is_utilized=False)
        except OTPLog.DoesNotExist:
            raise ValidationError({"code": "OTP Validation Failed"})

        log.is_utilized = True
        log.save()

        return self.build_data(log.creator)


class JWTAuthenticationSerializer(TokenRefreshSerializer, JWTResponseSerializer):

    def validate(self, attrs):
        super().validate(attrs)
        refresh = self.token_class(attrs["refresh"])
        user = DDUser.objects.get(pk=refresh.payload.get('user_id'))
        return self.build_data(user)


class DDUserUpdateInlineSerializer(serializers.ModelSerializer):

    class Meta:
        model = DDUser
        fields = ["username", "id", "first_name", "last_name"]
        read_only = ["username", "id", "first_name", "last_name"]


class FCMTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = FCMTokens
        fields = ['token', 'device']
