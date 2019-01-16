#!/usr/bin/python3
# -*- coding: utf-8 -*-
import copy
import datetime

from sqlalchemy import MetaData
from data_transmission.application.helper import json_dumps
from data_transmission.application.helper.run import wrapper
from data_transmission.sdk.db import DBEngines
from data_transmission.sdk.db import DBOption
from data_transmission.application.helper.mysql_tables import metadata, Table
from data_transmission.application.helper import LOG_WARNING


def current_level(db_url):
    level = 0
    sql = "select node_id from current_node"
    with DBOption(url=db_url) as session:
        res = session.execute(sql)
    if res:
        for each in res:
            level = each[0] if each else 0
    level = str(level)
    return level


def current_level_code(db_url):
    level = current_level(db_url)
    level = int(level)
    current_node_level = None
    if level == 1:
        node_level = "ONE"
    elif level == 2:
        node_level = "TWO"
    elif level == 3:
        node_level = "THREE"
    else:
        node_level = "FOR"
    sql = "select node_code from node where node_level='{}'".format(node_level)
    with DBOption(url=db_url) as session:
        res = session.execute(sql)
    if res:
        for each in res:
            current_node_level = each[0] if each else 0
    return current_node_level, level


def es_history_time(db_url):
    sql = "select typeof from transmission_exception where typeof='{}'".format("file")
    with DBOption(url=db_url) as session:
        res = session.execute(sql)
    if res.rowcount > 0:
        return True
    return None


class MysqlHelper(object):
    def __init__(self, db_url):
        self.db_url = db_url
        self.engine = DBEngines().get(self.db_url)
        self.metadata = MetaData(bind=self.engine)
        self.init_mysql()

    def init_mysql(self):
        try:
            metadata.create_all(self.engine)
        except Exception as ex:
            LOG_WARNING.error(u"创建transmission_exception表时发生错误，请检查数据库。")
            LOG_WARNING.error(u"错误原因为：{}".format(str(ex)))

    def query(self, sql):
        res = None
        try:
            with DBOption(url=self.db_url) as session:
                res = session.execute(sql)
        except Exception as ex:
            LOG_WARNING.error(u"查询数据时出错，错误原因为:{}".format(str(ex)))
            LOG_WARNING.error(u"查询语句为:{}".format(sql))
        return res

    def update(self, sql):
        try:
            with DBOption(url=self.db_url) as session:
                session.execute(sql)
                session.commit()
            return True
        except Exception as ex:
            LOG_WARNING.error(u"修改记录时出错，错误原因为:{}".format(str(ex)))
            LOG_WARNING.error(u"修改语句为:{}".format(sql))
        return False

    def insert(self, table_name, data):
        table = Table(table_name, metadata, autoload=True)
        try:
            with DBOption(url=self.db_url) as session:
                session.execute(table.insert(), data)
                session.commit()
            return True
        except Exception as ex:
            LOG_WARNING.error(u"插入记录时出错，错误原因为:{}".format(str(ex)))
            LOG_WARNING.error(u"插入语句为:{}".format(table.insert()))
        return False

    def query_except(self, task_id=None):
        table_name = "transmission_exception"
        if task_id:
            sql = "select * from {} where is_success={} and task_id='{}'".format(table_name, 0, task_id)
        else:
            sql = "select * from {} where is_success={}".format(table_name, 0)
        excepts = self.query(sql)
        return excepts

    def insert_record(self, task_id, send_params, typeof, success_flag, source):
        data = dict()
        sql = "select id from transmission_exception where task_id='{}'".format(task_id)
        is_exits = self.query(sql)
        if is_exits.rowcount > 0:
            return True
        data.setdefault("task_id", task_id)
        if isinstance(send_params, (dict, list)):
            send_params = json_dumps(send_params)
        data.setdefault("send_params", send_params)
        data.setdefault("typeof", typeof)
        data.setdefault("is_success", success_flag)
        data.setdefault("source", source)
        flag = self.insert("transmission_exception", data)
        return flag

    def set_except_flag(self, task_id, success_flag):
        """
        更新数据是否发送成功
        :param str task_id: 任务ID.
        :param int success_flag: 成功的标识 1成功 | 0失败.
        :return: 更新状态.
        """
        sql = "update transmission_exception set is_success={} where task_id='{}'".format(success_flag, task_id)
        flag = self.update(sql)
        return flag

    def query_update(self, server_name, version):
        sql = r"select * from software_update where server_name='{}' and version='{}'".format(server_name, version)
        records = self.query(sql)
        result = list()
        if records:
            for record in records:
                temp = dict()
                for key, val in record.items():
                    if key == "publish_time" or key == "upload_time":
                        val = str(val)
                    temp.setdefault(key, val)
                result.append(temp)
        return result

    def insert_update(self, task_id, typeof, records, source):
        temp_list = copy.deepcopy(records)
        if records:
            for record in records:
                if "id" in record:
                    record.pop("id")
                if "publish_time" in record:
                    publish_time = record.get("publish_time")
                    publish_time = datetime.datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")
                    record["publish_time"] = publish_time
                if "upload_time" in record:
                    upload_time = record.get("upload_time")
                    upload_time = datetime.datetime.strptime(upload_time, "%Y-%m-%d %H:%M:%S")
                    record["upload_time"] = upload_time
                # 将选择性更新的的is_update置为0
                if record.get("soft_state") == 10 or record.get("soft_state") == "10":
                    record["is_update"] = 0

            self.insert_record(task_id, temp_list, typeof, 0, source)

            flag = False
            for record in records:
                flag = wrapper(self.insert, "software_update", record)
            if flag:
                self.set_except_flag(task_id, 1)
        return True
