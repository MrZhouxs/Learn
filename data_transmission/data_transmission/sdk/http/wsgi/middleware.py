
import webob.dec

from ....sdk.http.wsgi.application import *


class Middleware(Application):
    @classmethod
    def factory(cls, global_config, **local_config):
        """ for paste require """
        def _factory(app):
            conf = global_config.copy()
            conf.update(local_config)
            return cls(app, **local_config)

        return _factory

    def __init__(self, application):
        self.application = application

    def process_request(self, request):
        return None

    def process_response(self, request, response):
        """Do whatever you'd like to the response, based on the request."""
        return response

    @webob.dec.wsgify(RequestClass=Request)
    def __call__(self, request):
        try:
            response = self.process_request(request)
            if response:
                return response
            response = request.get_response(self.application)
            return self.process_response(request, response)
        except Exception as e:
            return render_exception(e)
