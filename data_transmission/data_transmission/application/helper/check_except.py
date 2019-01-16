#!/usr/bin/python3
# -*- coding: utf-8 -*-
import copy

from data_transmission.application.helper import LOG_WARNING, json_loads
from data_transmission.application.helper.jpype_helper import JpypeHelper
from data_transmission.application.helper.file_operator import FileOperator
from data_transmission.application.helper.mysql_helper import MysqlHelper
from data_transmission.application.helper.elasticsearch_operator import ElasticsearchHelper
from data_transmission.application.helper.kafka_helper import KafkaHelper


class CheckExcept(object):
    def __init__(self, config, time_of_resend=10):
        self.db_url = config.get("db_url")
        self.es_config = config.get("elastic")
        self.kafka_config = config.get("kafka")
        self.kafka_host = self.kafka_config.get("host", "127.0.0.1")
        self.kafka_port = self.kafka_config.get("port", 9092)
        self.kafka_host = "{}:{}".format(self.kafka_host, self.kafka_port)
        self.jpype_object = JpypeHelper(self.db_url)
        self.file_operator = FileOperator()
        self.time_of_resend = time_of_resend
        self.mysql_obj = MysqlHelper(self.db_url)
        self.es_obj = ElasticsearchHelper(es_config=self.es_config, db_url=self.db_url)
        self.kafka_obj = KafkaHelper(db_url=self.db_url)
        self.mq_url = config.get("mq_url")
        self.source_queue = config.get("source_queue")

    def check(self, task_id=None):
        excepts = self.mysql_obj.query_except(task_id)
        if excepts:
            if excepts.rowcount > 0:
                for exception in excepts:
                    if exception:
                        source = None
                        typeof = None
                        send_params = None
                        for key, val in exception.items():
                            if key == "typeof":
                                typeof = val
                            elif key == "send_params":
                                send_params = val
                                send_params = json_loads(send_params)
                            elif key == "task_id":
                                task_id = val
                            elif key == "source":
                                source = val
                        # 如果时send，表明是发送端的问题，需要调用java接口冲洗发送
                        if source == "send":
                            if typeof == "file":
                                data = copy.deepcopy(send_params)
                                file_path = send_params.get("file_path")
                                file_name = send_params.get("current_file_name")
                                file_content = self.file_operator.read_file(file_name, file_path)
                                data["transmission_data"] = file_content
                                self.resend(task_id, typeof=typeof, kwargs=data)
                            else:
                                self.resend(task_id, typeof, send_params)
                        # 接收端接收数据异常，需要重新处理
                        else:
                            if typeof == "file":
                                file_path = send_params.get("file_path")
                                file_name = send_params.get("current_file_name")
                                file_content = self.file_operator.read_file(file_name, file_path)
                                self.es_obj.insert_into_es(task_id=task_id, data=file_content, send_params=send_params,
                                                           typeof=typeof, source=source)
                            elif typeof == "alarm":
                                topic = send_params.get("data").get("topic")
                                self.kafka_obj.send_to_kafka(task_id=task_id, data=send_params, type_of=typeof,
                                                             source=source, topic=topic, hosts=self.kafka_host)
                            elif typeof == "update":
                                self.mysql_obj.insert_update(task_id=task_id, typeof=typeof, records=send_params,
                                                             source=source)

    def resend(self, task_id, typeof, kwargs):
        try:
            kwargs["mq_url"] = self.mq_url
            kwargs["source_queue"] = self.source_queue
            flag = self.jpype_object.send(typeof=typeof, kwargs=kwargs, is_resend=True)
            if flag:
                self.mysql_obj.set_except_flag(task_id, 1)
        except Exception as ex:
            LOG_WARNING.error(u"重新发送数据发生错误，错误原因为:{}".format(str(ex)))

    def notice_message(self, task_id, status):
        if not isinstance(status, int):
            status = int(status)
        if status == 1:
            LOG_WARNING.info("task_id为{}的任务处理成功，将状态置为1")
            self.mysql_obj.set_except_flag(task_id, 1)
        else:
            self.check(task_id)

