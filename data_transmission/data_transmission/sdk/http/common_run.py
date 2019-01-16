# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from paste import deploy

from ...sdk.http import possible_topdir

from oslo_log import log
from oslo_config import cfg

CONF = cfg.CONF


def setup_config():
    # """CONF.log_config_append为oslo_log的setup直接使用"""
    # CONF.log_config_append = os.path.join(possible_topdir, 'etc', 'logging.conf')
    # log.setup(CONF, "archive")
    # # here can parse args
    pass


def initialize_application(module, paste_config_name, app_name):
    drivers = module.setup_backends()
    module.setup_config()

    paste_config_file = os.path.join(possible_topdir, 'etc', paste_config_name)

    try:
        application = deploy.loadapp('config:%s' % os.path.abspath(paste_config_file), name=app_name)

    except Exception as e:
        print(e.message)

    return application
