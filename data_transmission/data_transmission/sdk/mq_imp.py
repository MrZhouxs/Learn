"""mq implement package.

all mq implement class

MQService is implement mq server, support send message and consume message
MQRpcService is implement mq server, support call message

declare_queue is create or query queue
declare_exchange is create or query exchange
"""
import uuid

import pika

from ..sdk.common.exception import MyError


def declare_queue(channel, queue):
    """queue declare func.

    所属单元: 消息队列创建单元

    create a queue or get a queue info.

    :param pika.adapters.blocking_connection.BlockingChannel channel: connection channel
    :param QueueParameters queue: queue info

    :return: Method frame from the Queue.Declare-ok response
    :rtype: `pika.frame.Method` having `method` attribute of type
          `spec.Queue.DeclareOk`
    """
    if queue.passive:
        channel.queue_declare(queue.name, passive=queue.passive)
    else:
        channel.queue_declare(queue=queue.name,
                              passive=queue.passive,
                              durable=queue.durable,
                              exclusive=queue.exclusive,
                              auto_delete=queue.auto_delete,
                              arguments=queue.args)


def declare_exchange(channel, exchange):
    """exchange declare func.

    所属单元: 交换机创建单元

    This method creates an exchange if it does not already exist, and if
    the exchange exists, verifies that it is of the correct and expected
    class.

    :param pika.adapters.blocking_connection.BlockingChannel channel: connection channel
    :param ExchangeParameters exchange: exchange info

    :returns: Method frame from the Exchange.Declare-ok response
    :rtype: `pika.frame.Method` having `method` attribute of type
      `spec.Exchange.DeclareOk`

    """
    if exchange.passive is True:
        channel.exchange_declare(exchange=exchange.name, passive=exchange.passive)
    else:
        channel.exchange_declare(exchange=exchange.name,
                                 exchange_type=exchange.exchange_type,
                                 passive=exchange.passive,
                                 durable=exchange.durable,
                                 auto_delete=exchange.auto_delete,
                                 arguments=exchange.args)


class MQService(object):
    """mq service class.

    所属单元: 消息通道申请单元、消息统计单元

    create a  mq service, can consumer message, and can publish message.

    Example of creating a MQService:

        # Create our connection object
        server = MQService(...)
    """

    def __init__(self, url, exchange=None, queue=None, routing_key=None, channel_params=None):
        """init func.

        所属单元: 路由器创建单元、路由绑定单元

        :param str url: mq connect url
        :param ExchangeParameters exchange: mq exchange parameter
        :param QueueParameters queue: mq queue parameter
        :param str routing_key: routing key
        :param ChannelParameters channel_params: connection channel info

        """
        self.url = url
        self.routing_key = routing_key or ''

        self.exchange = exchange
        self.queue = queue
        self.channel_params = channel_params

        self.count = 0
        self.exchange_name = ''
        self.queue_name = ''

        self.channel = None
        self.connection = None
        self.start_connection()
        # self.connection()

    def start_connection(self):
        # create connect and get channel
        self.connection = pika.BlockingConnection(pika.URLParameters(url=self.url))
        self.channel = self.connection.channel()

        if self.exchange and self.exchange.name:
            # exchange is use
            # create exchange
            self.exchange_name = self.exchange.name
            declare_exchange(self.channel, self.exchange)

            if self.queue and self.queue.name:
                # create queue
                self.queue_name = self.queue.name
                declare_queue(self.channel, self.queue)
            else:
                temp_queue = self.channel.queue_declare(exclusive=True)
                self.queue_name = temp_queue.method.queue

            # bing exchange and queue, use routing key
            self.channel.queue_bind(self.queue_name, self.exchange_name, self.routing_key)

        elif self.queue and self.queue.name:
            # only queue use
            # create queue
            self.queue_name = self.queue.name
            declare_queue(self.channel, self.queue)
        else:
            # raise Exception('no queue declare')
            # possible only mq client
            pass

        if self.channel_params:
            # Specifies a prefetch count window in terms of whole messages
            self.channel.basic_qos(prefetch_count=self.channel_params.qos)

    def close(self):
        """close server."""

        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.close()

    def basic_publish(self, exchange_name, routing_key, message, props=None):
        """publish message func.

        所属单元: 消息封装发送单元、路由判定单元

        Publish to the channel with the given exchange, routing key and body.
        Returns a boolean value indicating the success of the operation.

        NOTE: mandatory and immediate may be enabled even without delivery
          confirmation, but in the absence of delivery confirmation the
          synchronous implementation has no way to know how long to wait for
          the Basic.Return or lack thereof.

        :param exchange_name: The exchange to publish to
        :type exchange_name: str or unicode
        :param routing_key: The routing key to bind on
        :type routing_key: str or unicode
        :param message: The message body; empty string if no body
        :type message: str or unicode
        :param pika.spec.BasicProperties props: message properties

        :returns: True if delivery confirmation is not enabled (NEW in pika
            0.10.0); otherwise returns False if the message could not be
            delivered (Basic.nack and/or Basic.Return) and True if the message
            was delivered (Basic.ack and no Basic.Return)
        """
        return self.channel.basic_publish(exchange=exchange_name,
                                          routing_key=routing_key,
                                          body=message,
                                          properties=props,
                                          mandatory=True)

    def ack(self, delivery_tag, multiple=False):
        """ack message func.

        Acknowledge one or more messages. When sent by the client, this
        method acknowledges one or more messages delivered via the Deliver or
        Get-Ok methods. When sent by server, this method acknowledges one or
        more messages published with the Publish method on a channel in
        confirm mode. The acknowledgement can be for a single message or a
        set of messages up to and including a specific message.

        :param int delivery_tag: The server-assigned delivery tag
        :param bool multiple: If set to True, the delivery tag is treated as
                              "up to and including", so that multiple messages
                              can be acknowledged with a single method. If set
                              to False, the delivery tag refers to a single
                              message. If the multiple field is 1, and the
                              delivery tag is zero, this indicates
                              acknowledgement of all outstanding messages.
        """
        try:
            self.channel.basic_ack(delivery_tag, multiple)
            self.count += 1
        except Exception as ex:
            print(ex)
            raise MyError(ex)


class MessageCount(object):
    """message count calc implement class.

    所属单元: 消息统计单元

    implement a static class, can calc message by exchange, queue and routing key.

    Attributes:
        stat_info: the message calc count dict.

    """

    stat_info = dict()

    @staticmethod
    def add(exchange_name, queue_name, routing_key):
        """add a message calc.

        :param str exchange_name: exchange name
        :param str queue_name: queue name
        :param str routing_key: routing key name
        """
        if exchange_name:
            if exchange_name not in MessageCount.stat_info:
                MessageCount.stat_info[exchange_name] = 0
            MessageCount.stat_info[exchange_name] += 1

        if queue_name:
            if queue_name not in MessageCount.stat_info:
                MessageCount.stat_info[queue_name] = 0
            MessageCount.stat_info[queue_name] += 1

        if routing_key:
            if routing_key not in MessageCount.stat_info:
                MessageCount.stat_info[routing_key] = 0
            MessageCount.stat_info[routing_key] += 1


class MQRpcService(object):
    """MQ rpc service implement class.

    所属单元: 消息统计单元

    create a  mq rpc service, and can publish message and receive return.

    Example of creating a MQRpcService:

        # Create our connection object
        server = MQRpcService(...)

        ret = server.call_message(...)
    """

    def __init__(self, url):
        """init func.

        所属单元: 路由器创建单元、路由绑定单元

        :param str url: mq server connect url
        """
        self.url = url
        self.connection = pika.BlockingConnection(pika.URLParameters(url=self.url))
        self.channel = self.connection.channel()
        self.count = 0

        temp_queue = self.channel.queue_declare(exclusive=True)
        self.callback_queue = temp_queue.method.queue
        self.channel.basic_consume(consumer_callback=self.callback_on_response,
                                   no_ack=True,
                                   queue=self.callback_queue)

        self.response = None
        self.corr_id = None

    def close(self):
        """close mq connection and channel."""
        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.close()

    def call_message(self, exchange_name, routing_key, message):
        """send message and get return.

        所属单元: 消息封装发送单元、路由判定单元

        Publish to the channel with the given exchange, routing key and body.
        Returns a boolean value indicating the success of the operation.

        NOTE: mandatory and immediate may be enabled even without delivery
          confirmation, but in the absence of delivery confirmation the
          synchronous implementation has no way to know how long to wait for
          the Basic.Return or lack thereof.

        :param exchange_name: The exchange to publish to
        :type exchange_name: str or unicode
        :param routing_key: The routing key to bind on
        :type routing_key: str or unicode
        :param message: The message body; empty string if no body
        :type message: str or unicode
        :param pika.spec.BasicProperties props: message properties

        :returns: True if delivery confirmation is not enabled (NEW in pika
            0.10.0); otherwise returns False if the message could not be
            delivered (Basic.nack and/or Basic.Return) and True if the message
            was delivered (Basic.ack and no Basic.Return)
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange=exchange_name,
                                   routing_key=routing_key,
                                   body=message,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id
                                   ),
                                   mandatory=True)
        self.count += 1

        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def callback_on_response(self, ch, method, props, body):
        """callback queue consume func.

        callback queue consume thread, process callback message function.

        :param BlockingChannel ch: mq connection channel
        :param Deliver method: mq connection spec.Basic.Deliver
        :param BasicProperties props: mq return message properties
        :param str or unicode body: return message info
        """
        if self.corr_id == props.correlation_id:
            self.response = body
