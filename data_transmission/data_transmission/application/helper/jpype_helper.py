#!/usr/bin/python3
# -*- coding: utf-8 -*-
import copy
import os
import time

import jpype
from jpype import JClass
from oslo_log import log
from data_transmission.application.helper import json_dumps, LOG_WARNING, json_loads, get_queue
from data_transmission.application.helper.edit_model import EditModel
from data_transmission.application.helper.mysql_helper import MysqlHelper
from data_transmission.application.helper.run import wrapper
from data_transmission.sdk.mq import MQClient

LOG = log.getLogger("log")


class JpypeHelper(object):
    def __init__(self, db_url, jvm_path=None):
        self.edit_model = EditModel()
        if db_url:
            self.mysql_object = MysqlHelper(db_url)
        if jvm_path:
            self.jvm_path = jvm_path
        else:
            self.jvm_path = jpype.get_default_jvm_path()
        self.jar_main_path = "com.chinasoft.plugin.RabbitMq"
        self.init_jar()

    def init_jar(self):
        jar_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "etc", "plugin.jar")
        extra_jar_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "lib")
        jvm_args = list()
        jvm_args.append("-ea")
        jvm_args.append("-Djava.class.path={}".format(jar_path))        # jar路径
        jvm_args.append("-Djava.ext.dirs={}".format(extra_jar_path))    # 依赖包的路径
        jvm_args.append("-Dproperty=value")                             # 允许Java 应用需要设置或者获取 JVM 中的系统属性
        jvm_args.append("-Xmx1024M")                                     # jvm参数设置
        jvm_args.append("-Xms256m")
        jvm_args.append("-mx512m")
        try:
            if not jpype.isJVMStarted():
                jpype.startJVM(self.jvm_path, *jvm_args)
        except Exception as ex:
            LOG_WARNING.error(u"启动jvm失败，错误原因:{}".format(str(ex)))

    @staticmethod
    def get_jar_obj(path, kwargs=None):
        try:
            obj = JClass(path)
            if kwargs:
                return obj(kwargs)
            else:
                return obj()
        except Exception as ex:
            LOG_WARNING.error(u"初始化jar包出错，错误原因为:{}".format(str(ex)))
        return None

    def init_notice(self, mq, queue_name):
        mq_copy = copy.deepcopy(mq)
        if not isinstance(mq, dict):
            mq_copy = json_loads(mq_copy)
        mq_copy["queue"] = queue_name
        mq_str = json_dumps(mq_copy)
        try:
            obj = self.get_jar_obj(path=self.jar_main_path)
            obj.result(mq_str)
            LOG.info(u"成功初始化反馈接口")
        except Exception as ex:
            print(str(ex))
            LOG_WARNING.error(u"初始化反馈接口时发生异常，异常原因为：{}".format(str(ex)))

    def init_send(self, mq, queue_name):
        mq_copy = copy.deepcopy(mq)
        if not isinstance(mq, dict):
            mq_copy = json_loads(mq_copy)
        mq_copy["queue"] = queue_name
        mq_str = json_dumps(mq_copy )
        try:
            obj = self.get_jar_obj(path=self.jar_main_path)
            obj.send(mq_str)
            LOG.info(u"成功初始化发送接口")
        except Exception as ex:
            print(str(ex))
            LOG_WARNING.error(u"初始化发送接口时发生异常，异常原因为：{}".format(str(ex)))

    def receive_notice(self, mq, java_receive_queue, java_send_queue):
        mq_copy = copy.deepcopy(mq)
        if not isinstance(mq, dict):
            mq_copy = json_loads(mq_copy)
        mq2 = copy.deepcopy(mq_copy)
        mq_copy["queue"] = java_receive_queue
        mq2["queue"] = java_send_queue
        mq_copy = json_dumps(mq_copy)
        mq2 = json_dumps(mq2)
        try:
            obj = self.get_jar_obj(path=self.jar_main_path)
            obj.forward(mq_copy, mq2)
            LOG.info(u"成功初始化接收接口")
        except Exception as ex:
            LOG_WARNING.error(u"初始化反馈接口时发生异常，异常原因为：{}".format(str(ex)))

    def send_file(self, kwargs):
        params = self.edit_model.edit_file(kwargs)
        return params

    def send_stream(self, kwargs):
        params = self.edit_model.edit_string(kwargs)
        return params

    def send_by_jar(self, param):
        try:
            # 调用java接口发送数据
            LOG.info("调用java jar包的send方法")
            params_string = json_dumps(param)
            java_obj = self.get_jar_obj(path=self.jar_main_path)
            java_obj.send(params_string)
            time.sleep(2)
            return True
        except Exception as ex:
            LOG_WARNING.error(u"调用java发送接口发生异常，异常原因为:{}".format(str(ex)))
        return False

    def send(self, typeof, kwargs, is_resend=False):
        flag = False
        temp_kwargs = copy.deepcopy(kwargs)
        task_id = kwargs.get("task_id")
        mq_url = kwargs.get("mq_url")
        source_queue = kwargs.get("source_queue")
        typeof = typeof.lower()
        params = None
        if typeof == "file":
            params = self.send_file(kwargs)
        elif typeof == "alarm":
            params = self.send_stream(kwargs)
        elif typeof == "update":
            params = self.send_stream(kwargs)
        # 调用java方法发送数据
        if params:
            if typeof == "file":
                if "transmission_data" in kwargs:
                    temp_kwargs.pop("transmission_data")
            # 默认发送的数据的状态为失败状态0，在接收到任务成功的消息时，将状态置为成功1
            if not is_resend:
                self.mysql_object.insert_record(task_id, temp_kwargs, typeof, 0, "send")

            # flag = wrapper(self._send_by_mq, (params, mq_url, source_queue))
            self._send_by_mq(params, mq_url, source_queue)
        return flag

    def _send_by_mq(self, data, mq_url, queue_name):
        try:
            if not isinstance(data, str):
                data = json_dumps(data)
            MQClient.send_message(url=mq_url, exchange_name="", routing_key=queue_name, message=data)
            return True
        except Exception as ex:
            LOG_WARNING.error(u"mq消息发送失败，原因为:{}".format(str(ex)))
        return False

    def check_queue(self):
        """
        循环取检测队列是否有消息
        :param queue: 被检测的队列.
        :return:
        """
        while True:
            data = get_queue()
            if data:
                typeof = data.get("typeof")
                is_resend = data.get("is_resend")
                kwargs = data.get("kwargs")
                LOG.info(u"------------ 调用java接口发送数据:{} --------------------------".format(kwargs))
                self.send(typeof=typeof, kwargs=kwargs, is_resend=is_resend)
            else:
                time.sleep(5)

    @staticmethod
    def close_jvm():
        try:
            if jpype.isJVMStarted():
                jpype.shutdownJVM()
        except Exception as ex:
            LOG_WARNING.error(u"关闭jvm时发生错误，错误原因:{}".format(str(ex)))
