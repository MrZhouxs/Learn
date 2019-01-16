# !/user/bin/python3
# coding=utf-8
# @Time   : 2018/3/9/0009 15:10

import unittest
import pika

from ping_collector.sdk.mq import QueueParameters
from ping_collector.sdk.mq import ChannelParameters
from ping_collector.sdk.mq_imp import declare_queue
from ping_collector.sdk.mq_imp import MQService
from ping_collector.sdk.mq import ExchangeParameters
from ping_collector.sdk.mq_imp import MQRpcService
from ping_collector.sdk.mq_imp import declare_exchange
from ping_collector.sdk.mq_imp import MessageCount
from ping_collector.sdk.mq import MQConsumerService


class TestQueueParameters(unittest.TestCase):
    """消息队列创建单元 单元测试

    """

    def test_init(self):
        """消息队列创建单元  单元测试.

        测试name、passive参数给定参数是否能创建出QueueParameters对象.
        :return:
        """
        queue_parameters = QueueParameters(name="name", passive=False, durable=False,
                                           exclusive=False, auto_delete=False, args=None)
        # assertEqual 判断first和second是否相等（值，类型）
        # msg:当不相等的时候，提供不想等说明
        self.assertEqual(type(queue_parameters.name), str,
                         msg="queue_parameters.name参数类型不是str类型")
        self.assertEqual(type(queue_parameters.passive), bool,
                         msg="queue_parameters.passive参数类型不是bool类型")
        self.assertEqual(type(queue_parameters.durable), bool,
                         msg="queue_parameters.durable参数类型不是bool类型")
        self.assertEqual(type(queue_parameters.exclusive), bool,
                         msg="queue_parameters.exclusive参数类型不是bool类型")
        self.assertEqual(type(queue_parameters.auto_delete), bool,
                         msg="queue_parameters.auto_delete参数类型不是bool类型")
        if queue_parameters.args is not None:
            self.assertEqual(type(queue_parameters.args), bool,
                             msg="queue_parameters.args参数类型不是bool类型")
        # 判断QueueParameters创建后的对象是否和QueueParameters是一样的对象类型
        self.assertTrue(queue_parameters, QueueParameters)

    def test_init2(self):
        """消息队列创建单元  单元测试.

        测试name、passive参数给定正确参数类型是否能创建出QueueParameters对象.
        :return:
        """
        queue_parameters = QueueParameters(name="name", passive=False, durable=False,
                                           exclusive=False, auto_delete=False, args=None)
        self.assertEqual(type(queue_parameters.name), str,
                         msg="queue_parameters.name参数类型不是str类型")
        self.assertEqual(type(queue_parameters.passive), bool,
                         msg="queue_parameters.passive参数类型不是bool类型")
        self.assertTrue(queue_parameters, "QueueParameters未成功创建")

    def test_init3(self):
        """消息队列创建单元  单元测试.

        测试name、passive参数给定错误参数类型是否能创建出QueueParameters对象.
        :return:
        """
        queue_parameters = QueueParameters(name=1, passive="False", durable=False,
                                           exclusive=False, auto_delete=False, args=None)
        self.assertEqual(type(queue_parameters.name), str,
                         msg="queue_parameters.name参数类型不是str类型")
        self.assertEqual(type(queue_parameters.passive), bool,
                         msg="queue_parameters.passive参数类型不是bool类型")
        self.assertTrue(queue_parameters, "QueueParameters未成功创建")

    def test_init4(self):
        """消息队列创建单元  单元测试.

        测试给定默认参数的值时，是否能创建出QueueParameters对象.
        :return:
        """
        queue_parameters = QueueParameters(name="name", passive=False, durable=False,
                                           exclusive=False, auto_delete=False, args=None)
        self.assertTrue(queue_parameters, "QueueParameters未成功创建")

    def test_init5(self):
        """消息队列创建单元  单元测试.

        测试不给定默认参数的值时，是否能创建出QueueParameters对象.
        :return:
        """
        queue_parameters = QueueParameters(name="name", passive=False)
        self.assertTrue(queue_parameters, "QueueParameters未成功创建")


class TestChannelParameters(unittest.TestCase):
    """消息队列创建单元 单元测试

    """
    def test_init(self):
        """消息队列创建单元 单元测试.

        测试给定int类型参数能否创建出ChannelParameters对象.
        :return:
        """
        channel_parameters = ChannelParameters(qos=2)
        self.assertEqual(type(channel_parameters.qos), int,
                         msg="queue_parameters.args参数类型不是int类型")
        self.assertTrue(channel_parameters, "未成功创建出channel_parameters对象")

    def test_init2(self):
        """消息队列创建单元 单元测试.

        测试给定不是int类型参数能否创建出ChannelParameters对象.
        :return:
        """
        channel_parameters = ChannelParameters(qos="2")
        self.assertEqual(type(channel_parameters.qos), int,
                         msg="queue_parameters.args参数类型不是int类型")
        self.assertTrue(channel_parameters, "未成功创建出channel_parameters对象")


class TestDeclareQueue(unittest.TestCase):
    """消息队列创建单元 单元测试

    """
    def test_declare_queue(self):
        """消息队列创建单元 单元测试.

        测试给定正确连接MQ句柄和name为QueueName队列信息，能否创建出名为QueueName消息队列
        :return:
        """
        mq_url = "amqp://admin:admin@192.168.31.254:5672"
        self.connection = pika.BlockingConnection(pika.URLParameters(url=mq_url))
        self.channel = self.connection.channel()
        self.queue = QueueParameters(name="QueueName", passive=False)
        declare_queue(channel=self.channel, queue=self.queue)

    def test_declare_queue2(self):
        """消息队列创建单元 单元测试.

        测试给定正确连接MQ句柄和name为111队列信息，能否创建出名为111消息队列
        :return:
        """
        mq_url = "amqp://admin:admin@192.168.31.254:5672"
        self.connection = pika.BlockingConnection(pika.URLParameters(url=mq_url))
        self.channel = self.connection.channel()
        self.queue = QueueParameters(name=111, passive=False)
        declare_queue(channel=self.channel, queue=self.queue)


class TestMQService(unittest.TestCase):
    """
    路由器创建单元、路由绑定单元、消息统计单元   测试
    """
    def setUp(self):
        self.exchange = ExchangeParameters(name="exchange", passive=False)
        self.queue = QueueParameters(name="queue", passive=False)
        self.mq_url = "amqp://admin:admin@127.0.0.1:5672"

    def test_init(self):
        """不给出routing_key，不会创建出路由器

        :return:
        """
        MQService(url=self.mq_url, exchange=self.exchange, queue=self.queue)

    def test_init2(self):
        """给出routing_key，创建出路由器

        :return:
        """
        MQService(url=self.mq_url, exchange=self.exchange, queue=self.queue, routing_key="123")


class TestMQRpcService(unittest.TestCase):
    """
    路由器创建单元、路由绑定单元、消息统计单元   测试
    """
    def setUp(self):
        self.mq_url = "amqp://admin:admin@127.0.0.1:5672"

    def test_init(self):
        """会创建临时路由

        :return:
        """
        MQRpcService(url=self.mq_url)


class TeatExchangeParameters(unittest.TestCase):
    """
    交换器创建单元 测试
    """
    def test_init(self):
        """测试name属性为str类型是否能创建出交换器

        :return:
        """
        exchange = ExchangeParameters(name="exchange_name", passive=True)
        self.assertEqual(type(exchange.name), str,
                         msg="name不是str类型")
        self.assertTrue(exchange, "未创建出实例")

    def test_init2(self):
        """测试name属性为非str类型是否能创建出交换器

        :return:
        """
        exchange = ExchangeParameters(name=123, passive=True)
        self.assertEqual(type(exchange.name), str,
                         msg="name不是str类型")
        self.assertTrue(exchange, "未创建出实例")


class Testdeclare_exchange(unittest.TestCase):
    """
    交换器创建单元 测试
    """
    def test_init(self):
        """测试passive为False情况下能否创建出交换器

        :return:
        """
        mq_url = "amqp://admin:admin@192.168.31.254:5672"
        self.connection = pika.BlockingConnection(pika.URLParameters(url=mq_url))
        self.channel = self.connection.channel()
        self.exchange = ExchangeParameters(name="exchange", passive=False)
        declare_exchange(self.channel, self.exchange)

    def test_init2(self):
        """测试passive为True情况下能否创建出交换器

        :return:
        """
        mq_url = "amqp://admin:admin@192.168.31.254:5672"
        self.connection = pika.BlockingConnection(pika.URLParameters(url=mq_url))
        self.channel = self.connection.channel()
        self.exchange = ExchangeParameters(name="exchange", passive=False)
        declare_exchange(self.channel, self.exchange)


class TestMessageCount(unittest.TestCase):
    """消息统计单元 单元测试

    """
    def setUp(self):
        """初始化测试参数

        """
        self.exchange = ExchangeParameters(name="exchange", passive=False)
        self.queue = QueueParameters(name="queue", passive=False)
        self.mq_url = "amqp://admin:admin@127.0.0.1:5672"

    def test_MessageCount_add(self):
        """MessageCount的add方法

        消息统计单元 测试给定路由情况下能否正常统计消息
        :return:
        """
        message_count = MessageCount()
        message_count.add(exchange_name="exchange", queue_name="queue", routing_key="123")
        info = message_count.stat_info
        print(info)

    def test_MQService_ack(self):
        """MQService的ack方法

        测试单条消息是否能够统计成功
        :return:
        """
        mq = MQService(url=self.mq_url, exchange=self.exchange, queue=self.queue, routing_key='key')
        flag = mq.basic_publish(exchange_name=self.exchange.name, routing_key='key', message='message')
        print(flag)
        mq.ack(delivery_tag=0)
        print(mq.count)

    def test_MQService_ack2(self):
        """MQService的ack方法

        测试多条消息是否能够统计成功
        :return:
        """
        mq = MQService(url=self.mq_url, exchange=self.exchange, queue=self.queue, routing_key='key')
        flag = mq.basic_publish(exchange_name=self.exchange.name, routing_key='key', message='message')
        print(flag)
        mq.ack(delivery_tag=0)
        mq.ack(delivery_tag=0)
        mq.ack(delivery_tag=0)
        mq.ack(delivery_tag=0)
        print(mq.count)

    def test_MQRpcService_call_message(self):
        """MQRpcService的call_message方法

        测试单条消息是否能够正常统计
        :return:
        """
        rpc = MQRpcService(url=self.mq_url)
        rpc.call_message(exchange_name="exchange", routing_key='key', message="message1")
        print(rpc.count)

    def test_MQRpcService_call_message2(self):
        """MQRpcService的call_message方法

        测试多条消息是否能够正常统计
        :return:
        """
        rpc = MQRpcService(url=self.mq_url)
        rpc.call_message(exchange_name="exchange", routing_key='key', message="message1")
        rpc.call_message(exchange_name="exchange", routing_key='key', message="message1")
        rpc.call_message(exchange_name="exchange", routing_key='key', message="message1")
        rpc.call_message(exchange_name="exchange", routing_key='key', message="message1")
        rpc.call_message(exchange_name="exchange", routing_key='key', message="message1")
        print(rpc.count)


class TestLuYouPanDuan(unittest.TestCase):
    """路由判定单元  单元测试

    """
    def setUp(self):
        """初始化测试参数

        """
        self.exchange = ExchangeParameters(name="exchange", passive=False)
        self.queue = QueueParameters(name="queue", passive=False)
        self.mq_url = "amqp://admin:admin@127.0.0.1:5672"

    def test_MQService_basic_publish(self):
        """MQService的basic_publish方法

        测试queue的routing_key与发送消息的routing_key一致的情况下，队列是否能接受消息
        :return:
        """
        mq = MQService(url=self.mq_url, exchange=self.exchange, queue=self.queue, routing_key='key')
        mq.basic_publish(exchange_name=self.exchange.name,
                         routing_key='key',
                         message='message')

    def test_MQService_basic_publish2(self):
        """MQService的basic_publish方法

        测试queue的routing_key与发送消息的routing_key不一致的情况下，队列是否能接受消息
        :return:
        """
        mq = MQService(url=self.mq_url, exchange=self.exchange, queue=self.queue, routing_key='key')
        mq.basic_publish(exchange_name=self.exchange.name,
                         routing_key='key2',
                         message='message')

    def test_MQRpcService_call_message(self):
        """MQRpcService的call_message方法

        测试临时queue能否接受指定routing_key的消息
        :return:
        """
        rpc = MQRpcService(url=self.mq_url)
        rpc.call_message(exchange_name="exchange", routing_key='key', message="message1")


class TestMQConsumerService(unittest.TestCase):
    """路由判定单元  单元测试

    """
    def setUp(self):
        """初始化测试参数

        """
        self.exchange = ExchangeParameters(name="exchange", passive=False)
        self.queue = QueueParameters(name="queue", passive=True)
        self.mq_url = "amqp://admin:admin@127.0.0.1:5672"

    def test_start_consumer(self):
        """MQConsumerService的start_consumer方法

        测试原有的消息队列绑定的routing_key与现在发送消息的的routing_key一致的情况，
        队列能否消费消息
        :return:
        """
        mq = MQConsumerService(url=self.mq_url, exchange=self.exchange, queue=self.queue,
                               routing_key="key")
        mq.start_consumer(auto_ack=True)

    def test_start_consumer2(self):
        """MQConsumerService的start_consumer方法

        测试原有的消息队列绑定的routing_key与现在发送消息的的routing_key一致的情况，
        队列能否消费消息
        :return:
        """
        mq = MQConsumerService(url=self.mq_url, exchange=self.exchange, queue=self.queue,
                               routing_key="key2")
        mq.start_consumer(auto_ack=True)


if __name__ == '__main__':
    unittest.main()
