
from webob import Request,Response
import webob.dec
import six
from six.moves import http_client
from oslo_serialization import jsonutils
import wsgiref.util


class BaseApplication(object):
    @classmethod
    def factory(cls, global_config, **local_config):
        return cls(**local_config)

    def __call__(self, environ, start_response):
        raise NotImplementedError('not implement __call__')


class Application(BaseApplication):
    @webob.dec.wsgify(RequestClass=Request)
    def __call__(self, req):
        arg_dict = req.environ['wsgiorg.routing_args'][1]
        action = arg_dict.pop('action')
        del arg_dict['controller']

        params = req.environ.get('openstack.context', {})
        params.update(arg_dict)

        method = getattr(self, action)
        params = self._normalize_dict(params)

        try:
            result = method(req, **params)
        except Exception as e:
            # e.code = 404
            # e.title = '__exception'
            return render_exception(e)#, context=req.context_dict)

        if result is None:
            return render_response(
                status=(http_client.NO_CONTENT,
                        http_client.responses[http_client.NO_CONTENT]))
        elif isinstance(result, six.string_types):
            return result
        elif isinstance(result, webob.Response):
            return result
        elif isinstance(result, webob.exc.WSGIHTTPException):
            return result

        response_code = self._get_response_code(req)
        return render_response(body=result,
                               status=response_code,
                               method=req.method)

    def _get_response_code(self, req):
        req_method = req.environ['REQUEST_METHOD']
        # controller = importutils.import_class('keystone.common.controller')
        # code = None
        # if isinstance(self, controller.V3Controller) and req_method == 'POST':
        #     code = (http_client.CREATED,
        #             http_client.responses[http_client.CREATED])
        code = None
        if req_method == 'POST':
            code = (http_client.CREATED,
                    http_client.responses[http_client.CREATED])
        return code

    def _normalize_arg(self, arg):
        return arg.replace(':', '_').replace('-', '_')

    def _normalize_dict(self, d):
        return {self._normalize_arg(k): v for (k, v) in d.items()}

    @classmethod
    def base_url(cls, context, endpoint_type):
        # url = CONF['%s_endpoint' % endpoint_type]
        #
        # if url:
        #     substitutions = dict(
        #         itertools.chain(CONF.items(), CONF.eventlet_server.items()))
        #
        #     url = url % substitutions
        # elif 'environment' in context:
        #     url = wsgiref.util.application_uri(context['environment'])
        #     # remove version from the URL as it may be part of SCRIPT_NAME but
        #     # it should not be part of base URL
        #     url = re.sub(r'/v(3|(2\.0))/*$', '', url)
        #
        #     # now remove the standard port
        #     url = utils.remove_standard_port(url)
        # else:
        #     # if we don't have enough information to come up with a base URL,
        #     # then fall back to localhost. This should never happen in
        #     # production environment.
        #     url = 'http://localhost:%d' % CONF.eventlet_server.public_port

        url = '/archive'
        return url.rstrip('/')



def render_response(body=None, status=None, headers=None, method=None):
    """Form a WSGI response."""
    if headers is None:
        headers = []
    else:
        headers = list(headers)
    headers.append(('Vary', 'X-Auth-Token'))

    if body is None:
        body = b''
        status = status or (http_client.NO_CONTENT,
                            http_client.responses[http_client.NO_CONTENT])
    else:
        content_types = [v for h, v in headers if h == 'Content-Type']
        if content_types:
            content_type = content_types[0]
        else:
            content_type = None

        if content_type is None or content_type in set(['application/json', 'application/json-home']):
            body = jsonutils.dump_as_bytes(body, cls=jsonutils.json.JSONEncoder)#, cls=utils.SmarterEncoder)
            if content_type is None:
                headers.append(('Content-Type', 'application/json'))
        if content_type is None:
            headers.append(('Content-Type', 'application/json'))

        status = status or (http_client.OK,
                            http_client.responses[http_client.OK])

    # NOTE(davechen): `mod_wsgi` follows the standards from pep-3333 and
    # requires the value in response header to be binary type(str) on python2,
    # unicode based string(str) on python3, or else keystone will not work
    # under apache with `mod_wsgi`.
    # keystone needs to check the data type of each header and convert the
    # type if needed.
    # see bug:
    # https://bugs.launchpad.net/keystone/+bug/1528981
    # see pep-3333:
    # https://www.python.org/dev/peps/pep-3333/#a-note-on-string-types
    # see source from mod_wsgi:
    # https://github.com/GrahamDumpleton/mod_wsgi(methods:
    # wsgi_convert_headers_to_bytes(...), wsgi_convert_string_to_bytes(...)
    # and wsgi_validate_header_value(...)).
    def _convert_to_str(headers):
        str_headers = []
        for header in headers:
            str_header = []
            for value in header:
                if not isinstance(value, str):
                    str_header.append(str(value))
                else:
                    str_header.append(value)
            # convert the list to the immutable tuple to build the headers.
            # header's key/value will be guaranteed to be str type.
            str_headers.append(tuple(str_header))
        return str_headers

    headers = _convert_to_str(headers)

    resp = webob.Response(body=body,
                          status='%d %s' % status,
                          headerlist=headers)

    # if method and method.upper() == 'HEAD':
    #     # NOTE(morganfainberg): HEAD requests should return the same status
    #     # as a GET request and same headers (including content-type and
    #     # content-length). The webob.Response object automatically changes
    #     # content-length (and other headers) if the body is set to b''. Capture
    #     # all headers and reset them on the response object after clearing the
    #     # body. The body can only be set to a binary-type (not TextType or
    #     # NoneType), so b'' is used here and should be compatible with
    #     # both py2x and py3x.
    #     stored_headers = resp.headers.copy()
    #     resp.body = b''
    #     for header, value in stored_headers.items():
    #         resp.headers[header] = value

    return resp


def render_exception(error, context=None, request=None, user_locale=None):
    """Form a WSGI response based on the current error."""

    # error_message = error.args[0]
    # message = oslo_i18n.translate(error_message, desired_locale=user_locale)
    # if message is error_message:
    #     # translate() didn't do anything because it wasn't a Message,
    #     # convert to a string.
    #     message = six.text_type(message)
    # body = {'error': {
    #     'code': error.code,
    #     'title': error.title,
    #     'message': message,
    # }}

    code = 404
    title = '__exception__'
    # message = 'exception msg is null'
    if 'code' in error:
        code = error.code
    if 'title' in error:
        title = error.title
    message = error.message
    body = {'error': {
        'code': code,
        'title': title,
        'message': message,
    }}
    headers = []
    # if isinstance(error, exception.AuthPluginException):
    #     body['error']['identity'] = error.authentication
    # elif isinstance(error, exception.Unauthorized):
    #     # NOTE(gyee): we only care about the request environment in the
    #     # context. Also, its OK to pass the environment as it is read-only in
    #     # Application.base_url()
    #     local_context = {}
    #     if request:
    #         local_context = {'environment': request.environ}
    #     elif context and 'environment' in context:
    #         local_context = {'environment': context['environment']}
    #     url = Application.base_url(local_context, 'public')
    #
    #     headers.append(('WWW-Authenticate', 'Keystone uri="%s"' % url))
    # return render_response(status=(error.code, error.title),
    #                        body=body,
    #                        headers=headers)
    return render_response(status=(code, title),
                           body=body,
                           headers=headers)

