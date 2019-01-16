#!/usr/bin/python3
# -*- coding: utf-8 -*-

from data_transmission.application.helper import file_model, string_model
from data_transmission.application.helper.mysql_helper import current_level


class EditModel(object):
    def __init__(self):
        pass

    def edit_file(self, kwargs):
        db_url = kwargs.pop("db_url")
        file_name = kwargs.pop("file_name")
        file_path = kwargs.pop("file_path")
        task_id = kwargs.pop("task_id")
        receivers = kwargs.pop("receivers")
        level = current_level(db_url)
        queue_name = kwargs.pop("queue_name")
        file_model["local_id"] = level                                  # 本地节点标识
        file_model["file_path"] = file_path                             # 文件路径
        file_model["file_name"] = file_name                             # 文件名陈，多个以,隔开
        file_model["task_id"] = task_id                                 # 唯一任务ID
        file_model["receive"] = self.edit_receiver(receivers, queue_name)      # 接收方信息
        file_model["send_sys_id"] = "high_level"                        # 发送方系统标识
        file_model["is_secret"] = 0                                     # 是否加密 1是 0否
        file_model["priority"] = "01"                                   # 优先级 00-10，00为未设置，01为最高,10为最低
        file_model["send_model"] = 0                                    # 发送模式 0：点对点；1：组播；2：广播
        file_model["secret_level"] = 0                                  # 密级 0：低；1：中；2：高
        file_model["data"] = kwargs                                     # 其他携带数据
        return file_model

    def edit_string(self, kwargs):
        task_id = kwargs.pop("task_id")
        receivers = kwargs.pop("receivers")
        queue_name = kwargs.pop("queue_name")
        msgdata = kwargs.pop("msgdata")
        string_model["task_id"] = task_id                               # 唯一任务ID
        string_model["send_sys_id"] = "high_level"                      # 发送方系统标识
        string_model["receive"] = self.edit_receiver(receivers, queue_name)  # 接收方信息
        string_model["priority"] = "01"                                 # 优先级 00-10，00为未设置，01为最高,10为最低
        string_model["secret_level"] = 0                                # 密级 0：低；1：中；2：高
        string_model["is_secret"] = 0                                   # 是否加密 1是 0否
        string_model["send_model"] = 0                                  # 发送模式 0：点对点；1：组播；2：广播
        string_model["data"] = kwargs                                   # 其他携带数据
        string_model["msgdata"] = msgdata
        return string_model

    def edit_receiver(self, receives, queue_name):
        result = list()
        if not isinstance(receives, list):
            receives = [receives]
        for receiver in receives:
            temp = dict()
            temp.setdefault("route_id", 0)                            # 路由标识 0：默认；多个路由逗号分隔（途径节点）
            temp.setdefault("receive_sys_id", 201010)                 # 接收方系统唯一标识
            temp.setdefault("target_id", 2)                           # 目标节点标识
            temp.setdefault("link_id", 0)                             # 链路标识 0：默认；10：地面宽带网；11-19：预留21：VSAT卫星网；22：C/Ku卫星网；23：CCTV卫星网
            rabbit_mq = self.edit_rabbitmq(receiver, queue_name)
            temp.setdefault("mq", rabbit_mq)
            result.append(temp)
        return result

    @staticmethod
    def edit_rabbitmq(host, queue_name):
        res = dict()
        res.setdefault("host", host)
        res.setdefault("port", 5672)
        res.setdefault("user", "admin")
        res.setdefault("password", "123456")
        res.setdefault("queue", queue_name)
        return res
