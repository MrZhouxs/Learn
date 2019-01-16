# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from oslo_config import cfg

from ....sdk.common import dependency
from ....sdk.http import wsgi

CONF = cfg.CONF
AUTH_TOKEN_HEADER = 'X-Auth-Token'


@dependency.requires('auth_service_api')
class Auth(wsgi.V3Controller):
    def __init__(self, *args, **kw):
        super(Auth, self).__init__(*args, **kw)
        # self.token_controllers_ref = token.controllers.Auth()
        # config.setup_authentication()

    def test(self, context, auth=None):
        return ''

    def authenticate_for_token(self, request):
        # 判断是否有此用户
        body = {}
        if request.body:
            body = json.loads(request.body)
        username = body["username"]
        password = body["password"]

        # create roken
        token = self.auth_service_api.generate_token(username, password)
        return token

    def delete_token(self, request):
        # 判断是否有此用户
        token = request.headers.get(AUTH_TOKEN_HEADER)

        # create roken
        token = self.auth_service_api.delete_token(token)
        return token
