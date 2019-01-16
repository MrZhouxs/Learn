
from common.auth import routers
import routes
from common import wsgi
import common


def auth_app_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    mapper = routes.Mapper()
    add_routers = []

    for module in [common.auth]:
        module.routers.append_routers(mapper, add_routers)

    return wsgi.ComposingRouter(mapper, add_routers)
