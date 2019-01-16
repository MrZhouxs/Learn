#! /usr/env/bin
#  -*- encoding:utf-8 -*-

import logging
import socket

from logstash import formatter


class Singleton(object):
    """Singleton pattern.

    base class, used to create Singleton pattern.
    """
    _instance = None
    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kw)
        return cls._instance


class ElectMaster(Singleton):
    """A class which elects avail-handler.

    Elect avail-handler from logstash handlers(list type).active_handler: elected avail-handler
    """
    def __init__(self):
        self.active_handler = None
        self.handler_index = 0
        self.elected = False

    def elect_active_handler(self, handlers):
        """elect avail-handle from handlers func.

        :param handlers: logstash handler list.
        :return: master logstash handers
        """
        # 初次进行avail-handler选举
        if not self.elected:
            self._elect_one_avail_handler(handlers)
        else:
            # active-handler 失去连接，重新选举avail-handler
            self._elect_one_avail_handler(handlers)
        self.elected = True
        return self.active_handler

    def _elect_one_avail_handler(self, handlers):
        """elect avail-handler func.

        :param handlers: logstash handler list.
        :return: no return
        """
        # 若active_handler是handlers中最后一个，且已失去连接，则从起始位置选举。
        end_handler_isavail = True
        if self.elected:
            if self.handler_index == len(handlers) - 1 and not self._conn_result(self.active_handler):
                self.handler_index = 0
                self.active_handler = None
                end_handler_isavail = False

        # 选择handler，并记录当前handler在handlers中的位置
        for index, handler in enumerate(handlers):
            # 当handler 不能使用时，只能从后面的handler中选举；

            if index < self.handler_index and end_handler_isavail:
                continue
            if self._conn_result(handler):
                self.active_handler = handler
                self.handler_index = index
                break

    def _conn_result(self, handler):
        """check handler if available

        :param handler: TCPLogstashHandler.
        :return: True or False.
        """
        conn_result = False
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sk.connect((handler.host, handler.port))
            conn_result = True
        except Exception:
            conn_result = False
        sk.close()
        return conn_result


class MyLogstashFormatter(formatter.LogstashFormatterBase):
    """
    define msg type to logstash.

    extends formatter.LogstashFormatterBase.
    """
    def format(self, record):
        """
        msg format
        :param record: accept msg record.
        :return: msg
        """
        # Create message dict
        message = {
            '@timestamp': self.format_timestamp(record.created)
            if hasattr(record, 'DATETIME') else self.format_timestamp(record.created),
            'host': self.host,
            'type': self.message_type,

            # Extra Fields
            'level': record.levelname,
            'logger_name': record.name,

        }

        # Add extra fields
        #message.update(self.get_extra_fields(record))
        message.update(eval(record.getMessage()))
        print('yyyyyy----------{}'.format(message))
        if hasattr(message, 'stack_info'):
            del record.stack_info
        # If exception, add debug info
        if record.exc_info:
            message.update(self.get_debug_fields(record))
        return self.serialize(message)


class ToLogstash(Singleton):
    """A class which help user send msg to logstash.

    """
    def __init__(self):
        self._logger = None
        self.appended_handlers = []

    def setlogger(self, name=None):
        """set logger name func.

        :param name: logger node.
        :return:
        """
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.INFO)

    def addHandler(self, handler):
        """add handler func.
        _logger has on handler most.
        :param handler: add handler.
        :return: no return.
        """
        if not handler in self.appended_handlers:
            self.appended_handlers.append(handler)

    def del_handler(self, handler):
        """del handler from appender-handlers.

        :return: no return
        """
        if handler in self.appended_handlers:
            self.appended_handlers.remove(handler)

    def init_sender(self):
        # 若_logger没有handler，则添加到_logger
        # handler = ElectMaster().elect_active_handler(self.appended_handlers)
        global elect_handler
        handler = elect_handler.elect_active_handler(self.appended_handlers)
        if not handler in self._logger.handlers:
            self._logger.handlers = []
            self._logger.addHandler(handler)

    def send_to_logstash(self, msg):
        """send msg to logstash func.

        :param msg: msg to logstash
        :return: send result.True or False.
        """
        self.init_sender()
        send_result = True
        if self._logger:
            if self._logger.handlers:
                try:
                    self._logger.info(msg)
                except:
                    send_result = False
            else:
                send_result = False
                print("logger has not handler")
        else:
            send_result = False
            print("undefined available logger")
        return send_result

elect_handler = ElectMaster()
logstash_sender = ToLogstash()
log_to_logstash_sender = ToLogstash()


def init_logstash_sender(tcphandlers, name):
    global logstash_sender
    logstash_sender.setlogger(name)
    for eachhandler in tcphandlers:
        eachhandler.formatter = MyLogstashFormatter()
        logstash_sender.addHandler(eachhandler)


def init_log_to_logstash_sender(tcphandlers, name):
    global log_to_logstash_sender
    log_to_logstash_sender.setlogger(name)
    for eachhandler in tcphandlers:
        eachhandler.formatter = MyLogstashFormatter()
        log_to_logstash_sender.addHandler(eachhandler)
