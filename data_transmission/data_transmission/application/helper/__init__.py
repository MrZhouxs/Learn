#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
from multiprocessing import Manager
from oslo_log import log

LOG_WARNING = log.getLogger()
manage = Manager()
queue = manage.Queue()


def put_queue(data):
    global queue
    try:
        queue.put(data)
    except Exception as ex:
        LOG_WARNING.error(u"数据存放在queue中发生异常，异常原因:{}".format(str(ex)))


def get_queue():
    global queue
    try:
        if queue.qsize() > 0:
            data = queue.get()
            return data
    except Exception as ex:
        LOG_WARNING.error(u"从queue中取数据时发生异常，异常原因为:{}".format(str(ex)))
    return None


def json_dumps(param):
    try:
        param = json.dumps(param)
        return param
    except Exception as ex:
        LOG_WARNING.error(u"将数据转化成json字符串时出错，错误原因为：{}".format(str(ex)))
    return False


def json_loads(param):
    try:
        param = json.loads(param)
        return param
    except Exception as ex:
        LOG_WARNING.error(u"将数据转换成json数据时发生错误，错误原因为:{}".format(str(ex)))
    return False


file_model = {
    "task_id": "100",
    "send_sys_id": "101010",
    "receive": [
        {
            "receive_sys_id": "201010",
            "target_id": "2",
            "link_id": "0",
            "route_id": "0"
        },
        {
            "receive_sys_id": "201011",
            "target_id": "3",
            "link_id": "0",
            "route_id": "0"
        }
    ],
    "file_path": "d:/file",
    "file_name": "1.txt",
    "local_id": "1",
    "secret_level": "0",
    "is_secret ": "0",
    "priority": "01",
    "send_model": "0",
    "data": ""
}

string_model = {
    "task_id": "100",
    "send_sys_id": "101010",
    "receive": [
        {
            "receive_sys_id": "201010,201012",
            "taget_id": "2",
            "link_id": "0",
            "route_id": "1,3,2"
        },
        {
            "receive_sys_id": "201011",
            "taget_id": "3",
            "link_id": "0",
            "route_id": "1,2,3"
        }
    ],
    "priority": "01",
    "secret_level": "0",
    "is_secret": "0",
    "msgdata": [],
    "send_model": "0",
    "data": ""
}