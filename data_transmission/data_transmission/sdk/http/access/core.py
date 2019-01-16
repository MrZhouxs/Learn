
import webob.dec
from oslo_log import log

from ....sdk.common import timeutils
from ....sdk.http.wsgi.middleware import Middleware

LOG = log.getLogger('access')
APACHE_TIME_FORMAT = '%d/%b/%Y:%H:%M:%S'
APACHE_LOG_FORMAT = (
    '%(remote_addr)s - %(remote_user)s [%(datetime)s] "%(method)s %(url)s '
    '%(http_version)s" %(status)s %(content_length)s %(return)s')


class AccessLogMiddleware(Middleware):

    @webob.dec.wsgify
    def __call__(self, request):
        data = {
            'remote_addr': request.remote_addr,
            'remote_user': request.remote_user or '-',
            'method': request.method,
            'url': request.url,
            'http_version': request.http_version,
            'status': 500,
            'content_length': '-'}

        try:
            response = request.get_response(self.application)
            data['status'] = response.status_int
            data['content_length'] = len(response.body) or '-'
            # data['return'] = str(response.body, encoding='utf-8')
            data['return'] = response.body.decode('unicode_escape')
        finally:
            now = timeutils.utcnow()
            data['datetime'] = '%s %s' % (now.strftime(APACHE_TIME_FORMAT),
                                          now.strftime('%z') or '+0000')
        try:
            LOG.info(APACHE_LOG_FORMAT % data)
            # LOG.warning(APACHE_LOG_FORMAT % data)
        except Exception as e:
            logg = ''
            logg = 'gg'

        return response
