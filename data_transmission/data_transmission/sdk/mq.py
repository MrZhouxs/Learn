"""mq process package.

all mq process class

MQClient is implement send message to mq, is a productor
MQConsumerService is implement consumer func, is a consumer
QueueParameters is save queue info
ExchangeParameters is save exchange info
ChannelParameters is save channel info
"""
import pika
import time
import os
import multiprocessing
from oslo_log import log
from pika import BasicProperties
from ..sdk.common import start_thread,start_process,stop_process
from ..sdk.common.exception import MyError
from ..sdk.mq_imp import MQService, MQRpcService

LOG = log.getLogger('log')

class MQClient(object):
    """MQ send message client class.

    所属单元: 请求获取解析单元、消息封装发送单元

    send message is asynchronous mode, no return object
    call message is synchronous mode, have return object

    """

    @staticmethod
    def send_message(url, exchange_name, routing_key, message, expiration="60000"):
        """static method, send message to mq, no return.

        :param str url: mq server curl
        :param str exchange_name: exchange name
        :param str routing_key: the routing key
        :param message: The message body; empty string if no body
        :type message: str or unicode
        :param str expiration: expiration time, ms, default 60 seconds
        :return: no return

        """
        mq_service = None
        try:
            mq_service = MQService(url=url)
            mq_service.start_connection()
            return mq_service.basic_publish(exchange_name, routing_key, message,
                                            props=BasicProperties(expiration=expiration))
        except Exception as ex:
            print(ex)
        finally:
            if mq_service:
                mq_service.close()

    @staticmethod
    def call_message(url, exchange_name, routing_key, message):
        """static method, call message to mq, have return info.

        :param str url: mq server curl
        :param str exchange_name: exchange name
        :param str routing_key: the routing key
        :param message: The message body; empty string if no body
        :type message: str or unicode
        :return: return object str or unicode

        """
        mq_service = None
        try:
            mq_service = MQRpcService(url=url)
            return mq_service.call_message(exchange_name, routing_key, message)
        finally:
            if mq_service:
                mq_service.close()


class QueueParameters(object):
    """queue parameters info, only save parameters.

    所属单元: 消息队列创建单元

    Attributes:
        name: queue name.
        passive: Only check to see if the queue exists.
        durable: Survive reboots of the broker
        exclusive: Only allow access by the current connection
        auto_delete: Delete after consumer cancels or disconnects
        args: Custom key/value arguments for the queue
    """

    def __init__(self, name, passive, durable=False, exclusive=False, auto_delete=False, args=None):
        """init func.

        Declare queue, create if needed. This method creates or checks a
        queue. When creating a new queue the client can specify various
        properties that control the durability of the queue and its contents,
        and the level of sharing for the queue.

        Leave the queue name empty for a auto-named queue in RabbitMQ

        :param name: The queue name
        :type name: str or unicode; if empty string, the broker will create a
          unique queue name;
        :param bool passive: Only check to see if the queue exists
        :param bool durable: Survive reboots of the broker
        :param bool exclusive: Only allow access by the current connection
        :param bool auto_delete: Delete after consumer cancels or disconnects
        :param dict args: Custom key/value arguments for the queue

        """
        self.name = name
        self.passive = passive
        self.durable = durable
        self.exclusive = exclusive
        self.auto_delete = auto_delete
        self.args = args


class ExchangeParameters(object):
    """exchange parameters info, only save parameters.

    所属单元: 交换器创建单元

    Attributes:
        name: The exchange name consists of a non-empty sequence of
                these characters: letters, digits, hyphen, underscore,
                period, or colon.
        exchange_type: The exchange type to use
        passive: Perform a declare or just check to see if it exists
        durable: Survive a reboot of RabbitMQ
        auto_delete: Remove when no more queues are bound to it
        args: Custom key/value pair arguments for the exchange
    """

    def __init__(self, name, passive, exchange_type='direct',
                 durable=False, exclusive=False, auto_delete=False, args=None):
        """init func.

        This method creates an exchange if it does not already exist, and if
        the exchange exists, verifies that it is of the correct and expected
        class.

        If passive set, the server will reply with Declare-Ok if the exchange
        already exists with the same name, and raise an error if not and if the
        exchange does not already exist, the server MUST raise a channel
        exception with reply code 404 (not found).

        :param name: The exchange name consists of a non-empty sequence of
                          these characters: letters, digits, hyphen, underscore,
                          period, or colon.
        :type name: str or unicode
        :param str exchange_type: The exchange type to use
        :param bool passive: Perform a declare or just check to see if it exists
        :param bool durable: Survive a reboot of RabbitMQ
        :param bool auto_delete: Remove when no more queues are bound to it
        :param dict args: Custom key/value pair arguments for the exchange
        """
        self.name = name
        self.passive = passive
        self.exchange_type = exchange_type
        self.durable = durable
        self.exclusive = exclusive
        self.auto_delete = auto_delete
        self.args = args


class ChannelParameters(object):
    """channel parameters info, only save parameters.

    所属单元: 消息队列创建单元

    Attributes:
        qos: Specifies a prefetch window in terms of whole
                messages. This field may be used in
                combination with the prefetch-size field; a
                message will only be sent in advance if both
                prefetch windows (and those at the channel
                and connection level) allow it. The
                prefetch-count is ignored if the no-ack
                option is set in the consumer.
    """

    def __init__(self, qos):
        """init func.

        Specify quality of service. This method requests a specific quality
        of service. The QoS can be specified for the current channel or for all
        channels on the connection. The client can request that messages be sent
        in advance so that when the client finishes processing a message, the
        following message is already held locally, rather than needing to be
        sent down the channel. Prefetching gives a performance improvement.

        :param int qos: Specifies a prefetch window in terms of whole
                                   messages. This field may be used in
                                   combination with the prefetch-size field; a
                                   message will only be sent in advance if both
                                   prefetch windows (and those at the channel
                                   and connection level) allow it. The
                                   prefetch-count is ignored if the no-ack
                                   option is set in the consumer.
        """
        self.qos = qos


class MQConsumerService(MQService):
    """mq consumer service class.

    所属单元: 路由判定单元

    start consumer mq queue

    Attributes:
        proc: receive message, and process message function.

    Example of creating and consume a MQConsumerService::

        # Create our connection object
        consumer = MQConsumerService(...)

        # The returned object will be a synchronous channel
        consumer.start_consumer()

    """

    def __init__(self, url, exchange=None, queue=None, routing_key=None,
                 channel_params=None, proc=None):
        """init func.

        :param str url: mq connect url
        :param ExchangeParameters exchange: mq exchange parameter
        :param QueueParameters queue: mq queue parameter
        :param str routing_key: routing key
        :param ChannelParameters channel_params: connection channel info
        :param callback proc: call back func, process message

        """
        super(MQConsumerService, self).__init__(url, exchange, queue, routing_key, channel_params)
        self.proc = proc
        self.is_stop = False
        self.auto_ack = False
        self._process = None
        # self.consumer_thread = None

    def start_consumer(self, auto_ack=False):
        """start consumer mq queue.

        :param bool auto_ack: is auto ack
        :return: no return

        """
        self.is_stop = False
        self.auto_ack = auto_ack
        mq_thread = start_thread('mq_consumer', self.__start_consuming)
        mq_thread.join()

        # self.consumer_thread = NewThread('mq_consumer', self.__start_consuming)
        # self.consumer_thread.start()

    def stop_consumer(self):
        """stop consumer mq queue."""
        self.is_stop = True
        if self.channel:
            self.channel.stop_consuming()

    def __start_consuming(self):
        """consume is delay func."""
        while not self.is_stop:
            try:
                self.start_connection()
                if self.channel:
                    self.channel.basic_consume(self.on_response, queue=self.queue_name, no_ack=self.auto_ack)
                self.channel.start_consuming()
                LOG.info('ffffffffffffffffffffffff')
                self.close()
                time.sleep(5)
            except Exception as ex:
                LOG.info(str(ex))
                LOG.info('---------------------------------------')
                # raise MyError(ex)

    def on_response(self, ch, method, properties, body):
        """get message.

        :param BlockingChannel ch: channel
        :param spec.Basic.Deliver method: deliver
        :param spec.BasicProperties properties: message pros
        :param str or unicode body: message info
        :return: no return

        """
        # print('[x] %r:%r' % (method.routing_key, body))
        response = None
        try:
            LOG.info('start execute mq msg......')
            response = self.proc(body)
            LOG.info('end  execute mq msg......')
        except Exception as ex:
            # print('mq message proc ex: ', ex)
            LOG.info('mq message proc ex:{}'.format(str(ex)))
            raise MyError(ex)
        if response and properties and properties.reply_to:
            ch.basic_publish(exchange='',
                             routing_key=properties.reply_to,
                             properties=pika.BasicProperties(
                                 correlation_id=properties.correlation_id),
                             body=str(response))

        self.ack(method.delivery_tag)
