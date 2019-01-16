
from ....sdk.common import dependency
from oslo_config import cfg
import os
import json

CONF = cfg.CONF


@dependency.provider('auth_service_api')
class AuthService(object):
    def __init__(self):
        # get all users
        CONF.users = dict()
        CONF.tokens = dict()
        # read config get users
        users_file = file(os.path.join(common.possible_topdir, 'etc', 'users.conf'))
        self.users_conf = json.load(users_file)

    def generate_token(self, name, password):
        if self.users_conf[name]["password"] == password:
            token = generate_auth_token(name)
            CONF.tokens[token] = name
            token_dict = dict()
            token_dict['token'] = token
            return token_dict
        else:
            raise Exception("not pass")

    def verify_token(self, token):
        if token in CONF.tokens:
            name = CONF.tokens[token]
            return verify_auth_token(name, token)
        raise Exception('token not exist.')

    def delete_token(self, token):
        if token in CONF.tokens:
            CONF.tokens.pop(token)
            return ""
        raise Exception('token not exist.')
