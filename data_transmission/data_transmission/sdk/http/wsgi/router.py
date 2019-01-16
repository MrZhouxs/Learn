
from webob import Request,Response
import webob.dec
import routes.middleware


class Router(object):
    """router implement class

    所属单元:

    """
    def __init__(self, mapper):
        self.mapper = mapper
        self._router = routes.middleware.RoutesMiddleware(self._dispatch,
                                                          self.mapper)

    # def __call__(self, environ, start_response):
    #     req = Request(environ)
    #     res = Response()
    #     print 'url = ', req.url
    #     print 'get = ', req.GET
    #     print 'body = ', req.body
    #     print req.path_info
    #
    #     result = self.mapper.match('/tasks/test')
    #     app = result['controller']
    #     action = result['action']
    #     method = getattr(app, action)
    #     result = method()
    #     return result

    @webob.dec.wsgify(RequestClass=Request)
    def __call__(self, req):
        return self._router

    @staticmethod
    @webob.dec.wsgify(RequestClass=Request)
    def _dispatch(req):
        """Dispatch the request to the appropriate controller.

        Called by self._router after matching the incoming request to a route
        and putting the information into req.environ.  Either returns 404
        or the routed WSGI app's response.

        """
        match = req.environ['wsgiorg.routing_args'][1]
        # if not match:
        #     return render_exception(
        #         exception.NotFound(_('The resource could not be found.')),
        #         user_locale=req.best_match_language())
        app = match['controller']
        return app


class ComposingRouter(Router):
    def __init__(self, mapper, routers):
        if mapper is None:
            mapper = routes.Mapper
        if routers is None:
            routers = []
        super(ComposingRouter, self).__init__(mapper)


