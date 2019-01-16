# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from oslo_config import cfg
from ....sdk.common import timeutils
from ....sdk.common import dependency


CONF = cfg.CONF
AUTH_TOKEN_HEADER = 'X-Auth-Token'


@dependency.requires('auth_service_api')
class PtTokenAuthMiddleware(Middleware):
    def process_request(self, request):
        # get token
        token = request.headers.get(AUTH_TOKEN_HEADER)

        # 查询获取token对应信息
        isok = self.auth_service_api.verify_token(token)
        if not isok:
            raise Exception("auth error ..... ")
