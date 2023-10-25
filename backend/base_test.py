import json
from urllib.parse import urlencode

from django.conf import settings
from django.test import TestCase
from mixer.backend.django import mixer
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import DDUser


class BaseAPIClient(APIClient):
    query: dict = {}
    path: str = NotImplemented

    def __init__(self, path):
        super().__init__()
        self.path = path

    def post_result(self, data: dict, path: str = None):
        response = self.post(path or self.path, data)
        return response

    def post_json_result(self, data: dict, path: str = None) -> dict:
        response = self.post_result(data, path)
        return json.loads(response.content)

    def get_json_result(self, path: str = None) -> dict:
        build_url = f'{path or self.path}?{urlencode(self.query)}'
        print(build_url)
        response = self.get(build_url)
        return json.loads(response.content)

    def result_count(self) -> int:
        result = self.get_json_result()
        data_count = len(list(result.get('data')))
        return result.get('total_count', data_count)


class JWTLoggedInAPIClient(BaseAPIClient):
    user: DDUser
    query: dict = {}

    def __init__(self, path):
        super().__init__(path)
        self.user: DDUser = mixer.blend(DDUser, is_staff=True)
        self.authenticate(self.user)

    def authenticate(self, user: DDUser):
        refresh = RefreshToken.for_user(user)
        self.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')


class LoggedOutUserTestCase(TestCase):
    path: str = NotImplemented
    client: BaseAPIClient

    def setUp(self) -> None:
        settings.OTP_PROVIDER_CLASS = 'users.tests.TestOTPGateway'
        self.client = BaseAPIClient(self.path)

    def login_user_with_mobile(self, mobile: str) -> dict:
        data = self.client.post_json_result({'mobile': mobile}, path="/otp/send/")
        token = data.get('data').get('token')
        return self.client.post_json_result({'token': token, 'code': 1111}, path="/login/validate_otp/")


class LoggedInUserTestCase(LoggedOutUserTestCase):
    client: JWTLoggedInAPIClient

    def setUp(self) -> None:
        self.client = JWTLoggedInAPIClient(self.path)