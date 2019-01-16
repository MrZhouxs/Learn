from common.auth import controllers


def append_routers(mapper, routers):
    auth_controller = controllers.Auth()

    mapper.connect('/test',
                   controller=auth_controller,
                   action='test',
                   conditions=dict(method=['GET']))

    mapper.connect('/authenticate_for_token',
                   controller=auth_controller,
                   action='authenticate_for_token',
                   conditions=dict(method=['POST']))

    mapper.connect('/delete_token',
                   controller=auth_controller,
                   action='delete_token',
                   conditions=dict(method=['GET']))
