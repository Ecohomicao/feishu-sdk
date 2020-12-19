# encoding: utf-8
"""
@author: liyao
@contact: liyao2598330@126.com
@software: pycharm
@time: 2020/6/11 6:10 下午
@desc:
"""
import sys
import json
import requests

from .Logs import logger
from .FeishuException import RequestException


class FeishuBase:
    retry = 3


class Request(FeishuBase):
    BASE_API_SERVER = 'https://open.feishu.cn/open-apis'

    def __init__(self, timeout=None, retry=None, **kwargs):
        self.port = 443
        self.protocol = "https"
        self.timeout = timeout
        self.verify = kwargs.get("verify", False)
        self.session = requests.Session()
        self.headers = {
            "Content-Type": "application/json"
        }

        self.app_access_token = None
        self.tenant_access_token = None

        self.retry = retry if retry else self.retry

        self.adapter = requests.adapters.HTTPAdapter(max_retries=self.retry)
        self.session.mount("https://", self.adapter)
        self.session.mount("http://", self.adapter)

    def get(self, url, data):
        return self.response(url, data, 'get')

    def post(self, url, data=None):
        return self.response(url, data, 'post')

    def file_post(self, url, data, files):
        return self.response(url, data, 'post', files)

    def response(self, url, data, method, files=None):
        if files is None:  # files情况下，data是不能转换为bytes的
            url = "%s%s" % (self.BASE_API_SERVER, url)
            if sys.version_info.major == 2:
                data = bytes(json.dumps(data)).encode(encoding='utf8')
            else:
                data = bytes(json.dumps(data), encoding='utf8')

            r = getattr(self.session, method)(url=url,
                                              headers=self.headers,
                                              data=data,
                                              timeout=self.timeout,
                                              verify=self.verify,
                                              ).json()
        else:
            temp = self.headers
            temp.pop("Content-Type")  # 此时的headers既包括Content-Type也有Authorization，所以把Content-Type去掉
            r = requests.post(
                url=url,
                headers=temp,
                files=files,
                data=data,
                stream=True,
                verify=self.verify).json()

        status_code = r.get('code', -1)
        if status_code != 0:
            raise RequestException(status=status_code, data=r.get('msg'))
        logger.debug('request url:%s; response:%s' % (url, r))
        return r
