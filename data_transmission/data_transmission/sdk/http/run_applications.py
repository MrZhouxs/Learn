# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

from ...sdk.http import common_run, possible_topdir, wsgi

from ...sdk import manage_rest
# import application
from ... import application
from ...application import *
from ...sdk import manage_rest


def serve(*servers):
    for server in servers:
        server.start()

    for server in servers:
        server.wait()


# if __name__ == '__main__':
def run_applications():
    """message application create func

    所属单元: 消息通道申请单元

    """
    common_run.setup_config()

    try:
        deploy_file = open(os.path.join(possible_topdir, 'etc', 'deploy.conf'))
        deploy_dict = json.load(deploy_file)

        servers = []
        for (k, v) in deploy_dict.items():
            print(k, v['host'], v['port'])
            module = eval(k)
            temp_app = common_run.initialize_application(module, v['config_file_name'], v['app_name'])
            server_temp = wsgi.Server(temp_app, v['host'], int(v['port']), threads=100)
            servers.append(server_temp)

        serve(*servers)
    except Exception as ex:
        print('run http applications ex ', ex)
        raise ex
