import itertools
import json
import uuid
from http import HTTPStatus

from base_test import LoggedOutUserTestCase, LoggedInUserTestCase
from django.conf import settings
from drone_destination.codes import ErrorCode
from drone_destination.otp_sender import OTPSender
from mixer.backend.django import mixer
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import DEVICES, DDUser
from users.utils import blacklist_user_refresh_tokens


def timelog_violation_action_in_test_run(user: DDUser):
    return str(uuid.uuid4())


class TestDocs(LoggedOutUserTestCase):

    def test_swagger_success(self):
        assert self.client.get('/swagger/').status_code == 200

    def test_redoc_success(self):
        assert self.client.get('/redoc/').status_code == 200


class TestOTPGateway(OTPSender):

    def __init__(self, mobile):
        super().__init__('http://localhost/', {}, mobile)

    def make_opt_request(self) -> dict:
        print(self.build_url)
        return {"code": 201, "status": "Success", "message": "Message sent successfully", "job_id": "631200030"}

    def code_generate(self) -> int:
        return 1111


class TestOTPSendView(LoggedOutUserTestCase):
    path = "/otp/send/"

    def test_fetch_valid_user_otp(self):
        users: list = mixer.cycle(10).blend(DDUser)
        profiles: list = mixer.cycle(len(users)).blend(creator=mixer.sequence(*users))
        user_profile = profiles[2]
        data = self.client.post_json_result({'mobile': user_profile.mobile}).get('data')
        assert data.get('token') is not None


class TestValidateOTPView(LoggedOutUserTestCase):
    path = "/login/validate_otp/"

    def test_validate_otp(self):
        user: DDUser = mixer.blend(DDUser)
        profile = mixer.blend(creator=user)
        response = self.login_user_with_mobile(profile.mobile)
        assert response.get('data').get('user').get('id') == user.pk


class TestAuthenticateView(LoggedOutUserTestCase):
    path = "/api/token/refresh/"

    def test_valid_authentication(self):
        user: DDUser = mixer.blend(DDUser)
        refresh = RefreshToken.for_user(user)
        response = self.client.post_json_result({"refresh": str(refresh)})
        assert response.get('data').get('user').get('id') == user.pk

    def test_fail_authentication(self):
        response = self.client.post_json_result({'refresh': 'some_fake_value'})
        assert response.get('error').get('error_code') == ErrorCode.INVALID_AUTH_TOKEN

    def test_fail_black_listed(self):
        user: DDUser = mixer.blend(DDUser)
        profile = mixer.blend(creator=user)
        data = self.login_user_with_mobile(profile.mobile)
        blacklist_user_refresh_tokens(user)
        response = self.client.post_json_result({"refresh": str(data.get('data').get('refresh'))})
        assert response.get('error').get('error_code') == ErrorCode.INVALID_AUTH_TOKEN


class TestFCMTokenView(LoggedInUserTestCase):
    path = "/fcm/token/"

    def test_fcm_token_added_success_response(self):
        response = self.client.post_result({'token': 'some_fake_token_for_testing_purpose', 'device': DEVICES.ANDROID})
        assert response.status_code == HTTPStatus.NO_CONTENT

    def test_fcm_token_not_added_with_fake_device_fields_error_response(self):
        response = self.client.post_json_result({'token': 'some_fake_token_for_testing_purpose', 'device': -1})
        return ErrorCode(response.get('error').get('error_code')).is_FIELDS_ERROR()
