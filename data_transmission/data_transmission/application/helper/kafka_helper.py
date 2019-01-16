#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import time

import kafka
from data_transmission.application.helper import LOG_WARNING
from data_transmission.application.helper.run import wrapper
from data_transmission.sdk.mq import MQClient
from data_transmission.application.helper.mysql_helper import MysqlHelper


class KafkaHelper(object):
    def __init__(self, db_url):
        self._kafka_producer = None
        self.mysql_obj = MysqlHelper(db_url)

    @staticmethod
    def _send_by_mq(data, kwargs):
        mq_url = kwargs.get("mq_url")
        queue_name = kwargs.get("queue_name")
        try:
            MQClient.send_message(url=mq_url, exchange_name="", routing_key=queue_name, message=data)
            return True
        except:
            LOG_WARNING.error(u"向rabbitmq发送数据失败，url为：{}".format(mq_url))
        return False

    def send_to_kafka(self, task_id, data, type_of, source, topic, hosts="127.0.0.1:9092"):
        self.mysql_obj.insert_record(task_id, send_params=data, typeof=type_of, source=source, success_flag=0)
        while not self._kafka_producer:
            self._kafka_producer = kafka.KafkaProducer(bootstrap_servers=hosts)
        flag = wrapper(self._send_to_kafka, data, topic)
        if flag:
            self.mysql_obj.set_except_flag(task_id, 1)

    def _send_to_kafka(self, data, topic):
        try:
            if not isinstance(data, str):
                data = json.dumps(data)
            if not isinstance(data, bytes):
                data = bytes(data, encoding="utf8")
            self._kafka_producer.send(topic=topic, value=data)
            time.sleep(1)
            return True
        except:
            LOG_WARNING.error(u"向Kafka的topic为{}发送数据失败".format(topic))
        return False
