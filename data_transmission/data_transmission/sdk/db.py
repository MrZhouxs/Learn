"""db process package.

all db process class.

AlchemyEncoder is implement json encoder
DBEngines is db process engines
DBSessions is sb process session
DBOption is a process implement for with ... do ...
"""
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import sessionmaker

from ..sdk.common import Singleton


# a base class for declarative class definitions.
DBBase = declarative_base()


class AlchemyEncoder(json.JSONEncoder):
    """json encoder implement class.

     extend this to recognize other objects, subclass and implement a
    ``.default()`` method with another method that returns a serializable
    object for ``o`` if possible, otherwise it should call the superclass
    implementation (to raise ``TypeError``).

    """

    def default(self, o):
        """default func.

        Implement this method in a subclass such that it returns
        a serializable object for ``o``, or calls the base implementation
        (to raise a ``TypeError``).

        For example, to support arbitrary iterators, you could
        implement default like this::

            def default(self, o):
                try:
                    iterable = iter(o)
                except TypeError:
                    pass
                else:
                    return list(iterable)
                # Let the base class default method raise the TypeError
                return JSONEncoder.default(self, o)

        """
        obj = o
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    if isinstance(data, datetime):
                        data = data.strftime('%Y-%m-%d %H:%M:%S')
                    json.dumps(data)  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError as ex:
                    print(ex)
                    fields[field] = None
                    # a json-encodable dict
            return fields
        return json.JSONEncoder.default(self, obj)


class AlchemyEncoderNew(json.JSONEncoder):
    """json encoder implement class.

     extend this to recognize other objects, subclass and implement a
    ``.default()`` method with another method that returns a serializable
    object for ``o`` if possible, otherwise it should call the superclass
    implementation (to raise ``TypeError``).

    """

    def default(self, o):
        """default func.

        Implement this method in a subclass such that it returns
        a serializable object for ``o``, or calls the base implementation
        (to raise a ``TypeError``).

        For example, to support arbitrary iterators, you could
        implement default like this::

            def default(self, o):
                try:
                    iterable = iter(o)
                except TypeError:
                    pass
                else:
                    return list(iterable)
                # Let the base class default method raise the TypeError
                return JSONEncoder.default(self, o)

        """
        obj = o
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    if isinstance(data, datetime):
                        data = data.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(data.__class__, DeclarativeMeta):
                        data = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
                    elif isinstance(data, list):
                        list_data = list()
                        for x in data:
                            if isinstance(x, datetime):
                                y = x.strftime('%Y-%m-%d %H:%M:%S')
                            elif isinstance(x.__class__, DeclarativeMeta):
                                y = json.dumps(x, cls=AlchemyEncoder, ensure_ascii=False)
                            json.dumps(y)
                            list_data.append(y)
                        data = list_data
                    json.dumps(data)  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError as ex:
                    print(ex)
                    fields[field] = None
                    # a json-encodable dict
            return fields
        return json.JSONEncoder.default(self, obj)


def json_change(o):
    """default func.

    Implement this method in a subclass such that it returns
    a serializable object for ``o``, or calls the base implementation
    (to raise a ``TypeError``).

    For example, to support arbitrary iterators, you could
    implement default like this::

        def default(self, o):
            try:
                iterable = iter(o)
            except TypeError:
                pass
            else:
                return list(iterable)
            # Let the base class default method raise the TypeError
            return JSONEncoder.default(self, o)

    """
    obj = o
    if isinstance(obj.__class__, DeclarativeMeta):
        # an SQLAlchemy class
        fields = {}
        for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
            data = obj.__getattribute__(field)
            try:
                if isinstance(data, datetime):
                    data = data.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(data.__class__, DeclarativeMeta):
                    data = json_change(data)
                elif isinstance(data, list):
                    list_data = list()
                    for x in data:
                        if isinstance(x, datetime):
                            y = x.strftime('%Y-%m-%d %H:%M:%S')
                        elif isinstance(x.__class__, DeclarativeMeta):
                            y = json_change(x)
                        json.dumps(y)
                        list_data.append(y)
                    data = list_data
                fields[field] = data
            except TypeError as ex:
                print(ex)
                fields[field] = None
                # a json-encodable dict
        return fields
    return None

# def new_alchemy_encoder():
#     _visited_objs = []
#
#     class AlchemyEncoder(json.JSONEncoder):
#         def default(self, obj):
#             if isinstance(obj.__class__, DeclarativeMeta):
#                 # don't re-visit self
#                 if obj in _visited_objs:
#                     return None
#                 _visited_objs.append(obj)
#
#                 # an SQLAlchemy class
#                 fields = {}
#                 for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
#                     data = obj.__getattribute__(field)
#                     try:
#                         if isinstance(data, datetime):
#                             data=data.strftime('%Y-%m-%d %H:%M:%S')
#                         json.dumps(data)
#  this will fail on non-encodable values, like other classes
#                         fields[field] = data
#                     except TypeError:
#                         fields[field] = None
#                 return fields
#
#             return json.JSONEncoder.default(self, obj)
#     return AlchemyEncoder


class DBEngines(metaclass=Singleton):
    """DB Engines manages, singleton class.

    所属单元: 数据库连接池建立单元

    Attributes:
        _engines: servers db engines.

    """

    def __init__(self):
        """init func, define _engines."""
        self._engines = dict()

    def get(self, url):
        """get a engine with db server.

        if no one, create a new engine

        :param str url: db server connect url
        :return: this db server engine

        """
        if url not in self._engines:
            engine = create_engine(url)
            self._engines[url] = engine

            # SSession = sessionmaker(bind=engine)
            # vvv = SSession()
            # vvv.q

        return self._engines[url]


class DBSessions(metaclass=Singleton):
    """DB Sessions marker manages, singleton class.

    所属单元: 数据库访问通道申请单元

    Attributes:
        _sessions: servers db session makers.

    """

    def __init__(self):
        """init func, define _sessions."""
        self._sessions = dict()

    def get(self, url):
        """get a session maker with db server.

        if no one, create a new session maker

        :param str url: db server connect url
        :return: this db server engine session maker
        """
        if url not in self._sessions:
            engine = DBEngines().get(url)
            session = sessionmaker(bind=engine)
            self._sessions[url] = session
        return self._sessions[url]


class DBOption(object):
    """db option class.

    所属单元: 数据库操作请求响应单元

    数据库操作提取封装单元 在 sqlalchemy Session 中

    use with ... do ...

    Attributes:
        _url: db connect url.
        session: session instance

    example:
        with DBOption(db_url) as session:
            session.exec(sql)
    """

    def __init__(self, url):
        """init func.

        :param str url: db server connect url

        """
        self._url = url
        self.session = None

    def __enter__(self):
        """with func return a session instance.

        :return: a session instance

        """
        session_maker = DBSessions().get(self._url)
        self.session = session_maker()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """with exit func.

        with ... do ...
        exec finished, if have exception db rollback

        :param exc_type: exception type
        :param exc_val: exception value
        :param exc_tb: exception

        """
        if exc_val:
            self.session.rollback()
            print('exec error ', exc_val)
        self.session.close()
