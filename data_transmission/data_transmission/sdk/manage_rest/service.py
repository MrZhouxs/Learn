"""
manage http factory for service implement
"""
import routes

from ...sdk.http import wsgi
from ...sdk.manage_rest import server_manage


def manage_app_factory(global_conf, **local_conf):
    """
    manage http implement factory
    :param global_conf: global config
    :param local_conf: local config
    :return: http example routers class
    """
    conf = global_conf.copy()
    conf.update(local_conf)

    mapper = routes.Mapper()
    add_routers = []

    for module in [server_manage]:
        module.routers.append_routers(mapper, add_routers)

    return wsgi.ComposingRouter(mapper, add_routers)

