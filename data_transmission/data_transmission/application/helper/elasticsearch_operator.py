#!/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime
import json

from elasticsearch import Elasticsearch, helpers
from data_transmission.application.helper.file_operator import FileOperator
from data_transmission.application.helper.mysql_helper import MysqlHelper
from data_transmission.application.helper import LOG_WARNING
from data_transmission.application.helper.run import wrapper


class ElasticsearchHelper(object):
    def __init__(self, es_config, db_url):
        if not es_config:
            es_config = {"host": "127.0.0.1", "port": 9200}
        self.es = self._init_es_connect(es_config)
        self.file_operator = FileOperator()
        self.mysql_obj = MysqlHelper(db_url)

    @staticmethod
    def _init_es_connect(es_config):
        username = es_config.pop('username') if 'username' in es_config else None
        password = es_config.pop('password') if 'password' in es_config else None
        if username and password:
            return Elasticsearch(hosts=[es_config], http_auth=(username, password))
        else:
            return Elasticsearch(hosts=[es_config])

    def query(self, es_query, index="s_cmm*", current_node_code=None):
        result = list()
        if current_node_code:
            query_temp = {"term": {"belong.deploy_level.keyword": {"value": current_node_code}}}
            es_query["query"]["bool"]["must"].append(query_temp)
        try:
            search_result = self.es.search(index=index, body=es_query)
            if "hits" in search_result:
                temp_data = search_result.get("hits")
                if "hits" in temp_data:
                    data = temp_data.get("hits")
                    # 取出主要数据
                    if not isinstance(data, list):
                        data = [data]
                    for each in data:
                        if "_source" in each:
                            _source = each.get("_source")
                            _index = each.get("_index")
                            _doc_type = each.get("_type")
                            format_data = {"_index": _index, "_type": _doc_type, "_source": _source}
                            result.append(format_data)
        except Exception as ex:
            LOG_WARNING.error(u"ES查询数据时错误，查询条件为:{}".format(es_query))
            LOG_WARNING.error(u"错误的原因为:{}".format(str(ex)))
        return result

    def save_data_to_file(self, file_name, file_path, history_times, current_node_code=None, limit_size=1000):
        result = list()
        es_queries = self.calculate_query_sentence(history_times)
        data_list = list()
        for each_es_query in es_queries:
            json_data = self.query(each_es_query, current_node_code=current_node_code)
            if json_data:
                data_list += json_data
        # 如果查询的数据不存在，不做处理
        if data_list:
            # 将10分钟的数据进行拆分
            split_data_list = self.split_data(data=data_list, limit_size=limit_size)
            for index, data in enumerate(split_data_list):
                temp_file_name = "{}_-{}.txt".format(file_name, index + 1)
                self.file_operator.save_file(data=data, file_name=temp_file_name, file_path=file_path)
                result.append(temp_file_name)
        return result

    @staticmethod
    def calculate_query_sentence(history_times):
        # 查询当前ES的数据，history_times为空的时候，查询当前所有ES的数据，不为空的时候，根据history_times查询往后的10min
        # 计算时间差，10min的数据以每分钟来查询，防止一次查询10min的数据超过10000条
        result = list()
        if history_times:
            now_time = datetime.datetime.now()
            for _ in range(0, 10):
                temp_time = now_time - datetime.timedelta(minutes=1)
                start_time = temp_time.strftime("%Y-%m-%d %H:%M:%S")
                end_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
                es_query = {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "range": {
                                        "public_field.datatime.keyword": {
                                            "gte": start_time,
                                            "lte": end_time
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "size": 10000
                }
                result.append(es_query)
                now_time = temp_time
        else:
            now_time = datetime.datetime.now()
            start_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
            es_query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "public_field.datatime.keyword": {
                                        "lte": start_time
                                    }
                                }
                            }
                        ]
                    }
                },
                "size": 10000
            }
            result.append(es_query)
        return result

    @staticmethod
    def split_data(data, limit_size=1000):
        """
        将每10分钟从ES查询的数据分隔开，避免文件过大.
        100条数据，大概1.2M.
        :param data: ES查询出的所有数据.
        :param limit_size: 每个文件的数据量.
        :return:
        """
        len_data = len(data)
        number = len_data // limit_size
        result = list()
        if data:
            if number == 0:
                result.append(data)
            else:
                index = 0
                for index in range(0, number):
                    result.append(data[index * limit_size: (index + 1) * limit_size])
                last_data = data[(index + 1) * limit_size:]
                if last_data:
                    result.append(last_data)
        return result

    def insert_into_es(self, task_id, data, send_params, typeof, source, es_handler=None):
        try:
            if data:
                self.mysql_obj.insert_record(task_id, send_params=send_params, typeof=typeof, success_flag=0, source=source)
                distinguish_data = self.distinguish_index(data=data)
                flag = None
                for es_index, es_data in distinguish_data.items():
                    if es_data:
                        flag = wrapper(self.bulk_insert, es_index, es_data, es_handler)
                        # self.bulk_insert(es_index=es_index, data=es_data, es_handler=es_handler)
                if flag:
                    self.mysql_obj.set_except_flag(task_id, 1)
        except Exception as ex:
            LOG_WARNING.error(u"读取文件数据，并将数据插入ES时出错，错误原因为:{}".format(str(ex)))

    def bulk_insert(self, es_index, data, es_handler=None):
        """
        批量插入数据到ES。
        :param str es_index: 待插入的ES的index.
        :param list data: 待批量插入的数据.
        :param es_handler: 测试时用.
        数据格式：[{"_index": index, "_type: type, "_source": source}, ...]
        :return:
        """
        try:
            if es_handler:
                es = self._init_es_connect(es_handler)
            else:
                es = self.es
            self.create_es_index(index=es_index, es=es)
            # 先去除重复数据
            # data = self.remove_duplicates(data)
            helpers.bulk(es, data)
            return True
        except Exception as ex:
            LOG_WARNING.error(u"批量插入数据到ES时发生错误，错误原因为:{}".format(str(ex)))
        return False

    @staticmethod
    def distinguish_index(data):
        """
        一次读取的文件内容中可能包含不同天的数据，要将数据区分出来.
        :param data: 一次读取的文件数据
        :return: 整理后的数据.
        """
        result = dict()
        if data:
            try:
                if isinstance(data, (bytes, str)):
                    data = json.loads(data)
            except json.JSONDecodeError:
                LOG_WARNING.error(u"ES数据格式有问题，丢弃该次数据.")
                return result
            if not isinstance(data, list):
                data = [data]
            for each in data:
                index = each.get("_index")
                if index in result:
                    result[index].append(each)
                else:
                    result.setdefault(index, [each])
        return result

    def create_es_index(self, index, es=None):
        # 为index设置容错率
        mapping = {
            "settings": {
                "index.mapping.ignore_malformed": True
            },
            "mappings": {
                "DEVICE": {
                    "properties": {
                        "GGQ": {"properties": {"FSSJ": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss"}}}}
                },
                "CHANNEL": {
                    "properties": {
                        "GGQ": {"properties": {"FSSJ": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss"}}}}
                },
                "DATA": {
                    "properties": {
                        "GGQ": {"properties": {"FSSJ": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss"}}}}
                },
                "BUSINESS": {
                    "properties": {
                        "GGQ": {"properties": {"FSSJ": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss"}}}}
                },
                "SOFTWARE": {
                    "properties": {
                        "GGQ": {"properties": {"FSSJ": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss"}}}}
                }

            }
        }
        try:
            if index:
                if es:
                    if not es.indices.exists(index=index):
                        es.indices.create(index=index, body=mapping)
                else:
                    if not self.es.indices.exists(index=index):
                        self.es.indices.create(index=index, body=mapping)
        except Exception as e:
            LOG_WARNING.warning('为{}的index设置settings出错，错误原因：{}'.format(index, str(e)))

    def remove_duplicates(self, es_data):
        es_query = {

        }
        self.es.search()
