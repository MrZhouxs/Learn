"""sdk package.

sdk common variant.

"""
import os

from oslo_config.cfg import CONF
from oslo_log import log

# application main dir, current file ../../
main_dir = os.path.normpath(os.path.join(os.path.abspath(__file__),
                                         os.pardir,
                                         os.pardir))

# parse and set log config file
CONF.log_config_append = os.path.join(main_dir, 'etc', 'logging.conf')
log.setup(CONF, "application")
