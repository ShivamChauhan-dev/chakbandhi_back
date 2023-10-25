import abc
from random import randint
from urllib.parse import urlencode

import requests
from django.conf import settings


class OTPSender(abc.ABC):
    build_url: str
    opt_code: int

    def __init__(self, url, para, mobile):
        self.opt_code = self.code_generate()
        para['message'] = f'Thank you for Sining up. Your OTP is {self.opt_code}. - G10'
        para['mobile'] = f'91{mobile}'
        self.build_url = f'{url}?{urlencode(para)}'

    @abc.abstractmethod
    def make_opt_request(self) -> dict:
        pass

    @abc.abstractmethod
    def code_generate(self) -> int:
        pass


class MakeMySMSOTPGateway(OTPSender):

    def __init__(self, mobile):
        provider_info: dict = settings.OTP_PROVIDER_INFO
        print(provider_info)
        super().__init__(provider_info.get('host'), provider_info.get('para'), mobile)

    def code_generate(self) -> int:
        return randint(1000, 9999)

    def make_opt_request(self) -> dict:
        content = requests.get(self.build_url).content
        return {'content': content}
