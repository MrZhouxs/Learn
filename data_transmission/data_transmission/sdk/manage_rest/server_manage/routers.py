"""
manage http routers package
"""
# -*- coding: utf-8 -*-
from ....sdk.manage_rest.server_manage import controllers


def append_routers(mapper, routers):
    """add http manage routers.

    所属单元: 请求获取解析单元

    :param mapper: global routes mapper
    :param routers: no use
    """

    task_controller = controllers.ManageController()

    mapper.connect('/tests',
                   controller=task_controller,
                   action='tests',
                   conditions=dict(method=['POST']))

    mapper.connect('',
                   controller=task_controller,
                   action='info',
                   conditions=dict(method=['POST']))

    mapper.connect('/',
                   controller=task_controller,
                   action='info',
                   conditions=dict(method=['POST']))

    mapper.connect('/start',
                   controller=task_controller,
                   action='start',
                   conditions=dict(method=['POST']))

    mapper.connect('/stop',
                   controller=task_controller,
                   action='stop',
                   conditions=dict(method=['POST']))

    mapper.connect('/restart',
                   controller=task_controller,
                   action='restart',
                   conditions=dict(method=['POST']))

    mapper.connect('/update',
                   controller=task_controller,
                   action='update',
                   conditions=dict(method=['POST']))

    mapper.connect('/test',
                   controller=task_controller,
                   action='test',
                   conditions=dict(method=['POST']))

    mapper.connect('/database_info',
                   controller=task_controller,
                   action='get_database_info',
                   conditions=dict(method=['POST']))

    mapper.connect('/process_start',
                   controller=task_controller,
                   action='process_start',
                   conditions=dict(method=['POST']))

    mapper.connect('/process_stop',
                   controller=task_controller,
                   action='process_stop',
                   conditions=dict(method=['POST']))

    mapper.connect('/test_connect',
                   controller=task_controller,
                   action='test_connect',
                   conditions=dict(method=['POST']))

