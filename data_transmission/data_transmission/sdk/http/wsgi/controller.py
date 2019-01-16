
from ....sdk.http.wsgi.application import Application


class V3Controller(Application):
    @classmethod
    def base_url(cls, context, path=None):
        endpoint = super(V3Controller, cls).base_url(context, 'public')
        if not path:
            path = cls.collection_name

        return '%s%s%s' % (endpoint, 'v3', path.lstrip('/'))

