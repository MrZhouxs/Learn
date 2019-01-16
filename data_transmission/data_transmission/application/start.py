# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""system start python file.

all start from Server class
work_func you can do implement your work

CollectorProcessTask is collect task implement
MQConsumerTask receive messages decode and run collect server
CollectorAnalyseTask is analyse task implement
MyHeartBeatTask is my new heart beat task implement
ManagerImp is my new http interface implement
"""
import copy
import datetime
import json
import platform
import time
import uuid
import os
import re
import configparser
import ast
import psutil
from logstash import TCPLogstashHandler
from oslo_log import log
from data_transmission.application.helper import json_loads, json_dumps
from data_transmission.sdk.mq import MQClient
from data_transmission.sdk.server_manager import Manager, Server, Task
from data_transmission.sdk.server_manager import HeartBeatTask
from data_transmission.sdk.common.commfunc import get_id, get_macs_ips
from data_transmission.sdk.update_helper.update_self import UpdateSelf
from data_transmission.sdk.server_manager import MQProcess, ProcessManage, KafkaTask
from data_transmission.application.helper.kafka_helper import KafkaHelper
from data_transmission.application.helper.elasticsearch_operator import ElasticsearchHelper
from data_transmission.application.helper.file_operator import FileOperator
from data_transmission.application.helper.jpype_helper import JpypeHelper
from data_transmission.application.helper.check_except import CheckExcept
from data_transmission.application.helper.download_helper import DownloadPackage
from data_transmission.application.helper.mysql_helper import current_level_code, es_history_time
from data_transmission.application.helper.mysql_helper import MysqlHelper


_MQ_CONSUMER = None
CONFIG = None
HOST_IP = None
HOST_PORT = None

LOG = log.getLogger('log')

LOG_WARNING = log.getLogger()
_SERVER_START_TIME = int(time.time())

SERVER_STATE = True

SERVER_UUID = str(uuid.uuid4())
LOG_TO_LOGSTASH_PORT = 8156

filepath = os.path.abspath(__file__)
filepath_split = filepath.split("/")
_SERVER_NAME = filepath_split[-4]


PACKAGE_PATH = None
ENV_PATH = None
ZOOKEEPER = None
_ENV_ARGS = None


FILEOPERATOR = FileOperator()
JPYPEHELPER = None
MYSQLHELPER = None
# 定义全局队列


class ManagerImp(Manager):
    """ manage server task processing controlled by http.

    task manage server,provide a group of interface that start stop and restart server's tasks.
    """
    def __init__(self):
        LOG.info("ManagerImp start")
        super(ManagerImp, self).__init__()
        self.env_args = _ENV_ARGS

    def start(self, body):
        """ start all task.

           start server's tasks

           :return:  1 成功
                    -1 传入格式错误

           """

        return "imp start"

    def stop(self, body):
        """stop all task.

        stop server's tasks.

        :return: 1 成功
                 -1 传入格式错误

        """

        return "imp stop"

    def restart(self):
        """restart all task.

        restart server's tasks.

        :return: imp restart
        :rtype: str
        """
        # self.stop()
        #
        # self.start()
        return 'imp restart'

    @staticmethod
    def process_start(body):
        """ start all task.

        start server's tasks

        :return:  1 成功
                 -1 传入格式错误

        """

        global _MQ_CONSUMER
        global CONFIG
        result = dict()
        if "process_num" in body:
            process_num = body["process_num"]

            if isinstance(process_num, str):
                process_num = int(process_num)
            for count in range(process_num):
                try:
                    _MQ_CONSUMER = MQConsumerTask(str(uuid.uuid4()), CONFIG)
                    ProcessManage().add_task(_MQ_CONSUMER)
                    ProcessManage().start(_MQ_CONSUMER.name())
                except Exception as e:
                    result["message"] = -1
                    result["error"] = "失败原因: %s,开启成功数：%d" % (e, count)
                    return result
            result["message"] = 1
            result["error"] = ""
        else:
            result["message"] = -2
            result["error"] = "失败原因: 传入格式错误"
        return result

    @staticmethod
    def process_stop(body):
        """stop all task.

        stop server's tasks.

        :return: 1 成功
                 -1 传入格式错误

        """
        result = dict()
        temp_pid = list()
        if "pid" in body and body["pid"] is not None:
            try:
                if not isinstance(body["pid"], list):
                    temp_pid.append(int(body["pid"]))
                    ProcessManage().stop(temp_pid)
                else:
                    ProcessManage().stop(body["pid"])
                result["message"] = 1
                result["error"] = ""
                return result
            except Exception as e:
                result["message"] = -1
                result["error"] = e

        else:
            result["message"] = -2
            result["error"] = "传入格式错误"
        return result

    def update(self, request):
        """
        /manage/update
        :param request:
        :return:
        """
        global _ENV_ARGS
        self.env_args = _ENV_ARGS
        response = dict()
        try:
            msg = json.loads(request.body.decode('utf-8'))
        except:
            response['result'] = 0
            response['msg'] = u'请求消息格式异常，无法处理'
            return response
        global CONFIG
        logstash_host = CONFIG['logstash_info']['host']
        handlers = list()
        for logstash_item in str(logstash_host).split(','):
            (host, port) = str(logstash_item).split(':')
            logstash_handler = TCPLogstashHandler(host, int(port),
                                                  version=1, message_type='logstash')
            handlers.append(logstash_handler)

        result = UpdateSelf(env_args=self.env_args, update_args=msg, handlers=handlers).update()

        if result:
            response['result'] = 0
            response['msg'] = result
            return response
        else:
            response['result'] = 1
            response['msg'] = '升级进程已启动'
            return response


class MyHeartBeatTask(HeartBeatTask):
    """ heartbeat report server.

    Report status information to monitor server.

    Attributes:
        start_time: task started time used for recording operating time
    """

    def __init__(self, config):
        """init heartbeat task.

        upload server state information to monitor server.

        :param config: server connection info
        """
        LOG.info("myheartbeat start")
        super(MyHeartBeatTask, self).__init__(config)
        self.start_time = _SERVER_START_TIME
        self.config = config

        self._version = self.get_version()
        self.node_path = ""

    def do(self, *args, **kwargs):
        """ inherit handler.

        make up a dict structure data,and put it to rabbit-mq no-callback queue.
        """
        global _SERVER_NAME
        msg = dict()
        msg['server_uuid'] = get_id("data_transmission")
        msg['server_type'] = "data_transmission"
        msg['server_version'] = self._version
        msg['server_state'] = 1
        msg['server_time'] = int(time.time()) - self.start_time
        msg['server_host_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

        pid_dict = self.get_process_status()
        msg['server_pid'] = pid_dict
        server_host_info = dict()
        server_host_info['cpu'] = psutil.cpu_percent(0)
        server_host_info['memory'] = psutil.virtual_memory().percent
        host_ips = list()
        mac_ip_info = get_macs_ips()
        for each in mac_ip_info:
            host_ips.append(mac_ip_info[each][-1])
        server_host_info['host_ip'] = host_ips
        msg['server_host_info'] = server_host_info

        global HOST_PORT
        global HOST_IP
        http_info = dict()
        http_info["server_ip"] = HOST_IP
        http_info["server_port"] = HOST_PORT
        msg['http_info'] = http_info

        database_info = dict()
        if 'db' in self._config:
            database_info['db_server_ip'] = self._config['db']['host']
            database_info['db_server_port'] = self._config['db']['port']
            database_info['db_user'] = self._config['db']['user']
            database_info['db_pwd'] = self._config['db']['password']
        msg['database_info'] = database_info

        cache_info = dict()
        if 'memcache' in self.config:
            cache_info['cache_server_ip'] = self._config['memcache']['host']
            cache_info['cache_server_port'] = self._config['memcache']['port']
        msg['cache_info'] = cache_info

        MQClient.send_message(
            self.config["mq_url"],
            exchange_name="",
            routing_key="server_state",
            message=json.dumps(msg))

    @staticmethod
    def get_version():
        location = os.path.realpath(__file__)
        if len(re.findall("-(\d\.\d\.\d?)-", location)) > 0:
            result = re.findall("-(\d\.\d\.\d?)-", location)[0]
            return result
        else:
            LOG.info("匹配失败没有找到版本号")
            return None

    @staticmethod
    def get_process_status():
        pid_status = list()
        killed_pid = list()
        process_dict = ProcessManage().get_task()
        for pid in process_dict.keys():
            temp_dict = dict()
            if type(pid) == int:
                try:
                    process = psutil.Process(pid)
                    if process.status().lower() == "zombie":
                        killed_pid.append(pid)
                    else:
                        temp_dict["pid"] = pid
                        temp_dict["status"] = process.status().lower()
                        pid_status.append(temp_dict)
                except:
                    killed_pid.append(pid)
            else:

                continue
        if killed_pid:
            ProcessManage().stop(killed_pid)

        for item in killed_pid:
            _, _ = os.waitpid(int(item), os.WNOHANG)
        return pid_status


class AlarmDataFromKafka(KafkaTask):
    """
    发送端从Kafka中获取告警数据并发送.
    """

    def __init__(self, name, config):
        self.db_url = config.get("db_url")
        self.kafka_config = config.get("kafka")
        self.kafka_host = self.kafka_config.get("host", "127.0.0.1")
        self.kafka_port = self.kafka_config.get("port", 9092)
        self.host = "{}:{}".format(self.kafka_host, self.kafka_port)
        # kafka的告警数据的topic
        self.topic = config.get("alarm_topic", "alarm-data")
        self.group_id = "AlarmDataFromKafkaGroupId"
        super(AlarmDataFromKafka, self).__init__(name, hosts=self.host, topic=self.topic, group_id=self.group_id)
        self.queue_name = config.get("send_queue", "data_transmission_send")
        # rabbitmq的url
        self.mq_url = config.get("mq_url")
        # 上报数据的目标节点的MQ信息
        self.high_level = config.get("high_level")
        self.current_node_level, self.level = current_level_code(self.db_url)
        self.source_queue = config.get("source_queue", "data_transmission_source")

    def do(self, message):
        # if self.level == 1 or self.level == "1":
        #     return
        try:
            task_id = str(uuid.uuid4())
            alarm_data = message.value
            if isinstance(alarm_data, bytes):
                alarm_data = alarm_data.decode('utf-8')
            alarm_data = json_loads(alarm_data)
            data = {"msgdata": alarm_data, "type": "alarm", "task_id": task_id, "queue_name": self.queue_name,
                    "receivers": self.high_level,
                    "mq_url": self.mq_url, "source_queue": self.source_queue}
            print("--------------- send alarm-data:{} --------------------".format(data))
            JPYPEHELPER.send("alarm", data)
        except Exception as ex:
            LOG_WARNING.error(u"发送端获取kafka中的告警数据时发生错误，错误原因为:{}".format(str(ex)))


class SendFileData(Task):
    """
    每隔10min查询ES的聚合、统计数据，并落地生成文件.
    """
    def __init__(self, name, config):
        interval = config.get("time_of_es_query", "10m")
        interval = self.calculate_time(interval)
        super(SendFileData, self).__init__(name, interval=interval)
        self.mq_url = config.get("mq_url")
        self.db_url = config.get("db_url")
        self.elastic_query_obj = ElasticsearchHelper(config.get("elastic"), config.get("db_url"))
        # 发送端保存文件的路径
        self.send_file_path = config.get("save_send_data", "/tmp/send_file")
        # 文件数据发送到rabbitmq的队列名
        self.queue_name = config.get("send_queue", "data_transmission_send")
        # 每个文件的数量
        self.each_file_number_of_es = config.get("number_of_es", "1000")
        # 上报数据的目标节点的MQ信息
        self.high_level = config.get("high_level")
        self.current_node_level, self.level = current_level_code(self.db_url)
        self.es_history_time = es_history_time(self.db_url)
        self.source_queue = config.get("source_queue", "data_transmission_source")

    def do(self):
        # if self.level == 1:
            # return
        try:
            # 以当前时间为文件名前缀
            now_time_string = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            file_name = now_time_string
            prefix = str(uuid.uuid4())
            file_path = os.path.join(self.send_file_path, prefix)
            # 将ES数据保存为本地文件
            file_names = self.elastic_query_obj.save_data_to_file(file_name, file_path, self.es_history_time,
                                                                  limit_size=self.each_file_number_of_es)
            list_file_names_str = ",".join(file_names)
            file_number = len(file_names)
            print("------------------ send file number {} ------------------------".format(file_number))
            for file_name in file_names:
                target_id = str(uuid.uuid4())
                file_content = FILEOPERATOR.read_file(file_name, file_path)
                # 拼接消息发送到rabbitmq
                data = {"file_name": list_file_names_str, "type": "file", "file_number": file_number,
                        "file_path": file_path, "task_id": target_id, "receivers": self.high_level,
                        "db_url": self.db_url, "current_file_name": file_name, "queue_name": self.queue_name,
                        "mq_url": self.mq_url, "source_queue": self.source_queue}
                data.setdefault("transmission_data", file_content)
                JPYPEHELPER.send("file", data)
        except Exception as ex:
            LOG_WARNING.error(u"发送端向rabbitmq发送文件时发生错误，错误原因为:{}".format(str(ex)))

    @staticmethod
    def calculate_time(time_of_query):
        """
        计算查询ES的时间间隔.
        :param time_of_query: 用户配置的时间.
               时间的格式为： xxx s(S), xxx m(M), xxx (H), xxx d(D)
        :return:
        """
        time_string = time_of_query[: len(time_of_query) - 1]
        try:
            time_int = int(time_string)
        except:
            LOG_WARNING.error(u"配置的ES查询时间格式错误，配置的时间为:{}".format(time_of_query))
            raise ValueError
        if "s" in time_of_query or "S" in time_of_query:
            result = time_int
        elif "m" in time_of_query or "M" in time_of_query:
            result = time_int * 60
        elif "h" in time_of_query or "H" in time_of_query:
            result = time_int * 60 * 60
        elif "d" in time_of_query or "D" in time_of_query:
            result = time_int * 60 * 60 * 24
        else:
            LOG_WARNING.error(u"配置的ES查询时间格式错误，配置的时间为:{}".format(time_of_query))
            raise ValueError
        return result


class SendVersionData(MQProcess):
    """
    发送rabbitmq中的升级信息给下级节点，并发送升级包.(发送端)
    """
    def __init__(self, name, config):
        url = config['mq_url'] if 'mq_url' in config else ''
        routing_key = config.get("update_queue", "update_server")
        queue_name = "transmission_update"
        self.mq_url = config.get("mq_url")
        # 升级包发送的队列名
        self.queue_name = config.get("send_queue", "data_transmission_send")
        self.package_save_path = config.get("send_update_package", "/tmp/send_package")
        # 单个文件的大小
        self.single_file_size = config.get("single_file_size", "1M")
        self.single_file_size_bytes = FILEOPERATOR.calculate_digits(self.single_file_size)
        super(SendVersionData, self).__init__(name, url, "", queue_name, routing_key=routing_key)
        self.download_obj = DownloadPackage()
        # 下级上报数据的目标节点的MQ信息
        self.low_level = config.get("low_level")
        self.source_queue = config.get("source_queue", "data_transmission_source")

    def do(self, body):
        """
        从rabbitmq接收升级信息信息.
        升级信息的格式为：
        {"type": "update", "data": [{"server_name": server_name, "version": new_version, "path": path}, ...]}
        :param body: rabbitmq messages.
        :return:
        """
        try:
            if isinstance(body, bytes):
                body = body.decode('utf-8')
            json_data = json.loads(body)
            task_id = str(uuid.uuid4())
            update_records = list()
            print("--------------- 收到的升级信息:{}".format(json_data))
            # 此处需要等待2秒，等待的是java端操作数据库，不能数据状态不对（强制更新的状态和选择性更新的状态）
            time.sleep(2)
            # 将升级信息发送给下级节点
            for each in json_data:
                server_name = each.get("server_name")
                version = each.get("version")
                records = MYSQLHELPER.query_update(server_name, version)
                update_records += records
            if update_records:
                data = {"msgdata": update_records, "type": "update", "task_id": task_id, "queue_name": self.queue_name,
                        "receivers": self.low_level, "case": json_data,
                        "mq_url": self.mq_url, "source_queue": self.source_queue}
                # format_data = {"typeof": "update", "kwargs": data, "is_resend": False}
                JPYPEHELPER.send("update", data)
        except Exception as ex:
            LOG_WARNING.error(u"发送端发送版本信息时发生错误，错误原因为:{}".format(str(ex)))


class MQConsumerTask(MQProcess):
    """MQ Consumer class.

    从rabbitmq告警队列中获取数据并发送到Kafka的topic为alarm-data中.

    Attributes:
        name: task name unique
        config: rabbit-mq connection info
    """

    def __init__(self, name, config):
        """ init func.

        inherit MQTak and overwrite a new callback function for the queue consumer.
        """

        url = config['mq_url'] if 'mq_url' in config else ''
        routing_key = config.get('receive_queue', "data_transmission_receive")
        queue_name = config.get("receive_queue", "data_transmission_receive")
        # queue_name = "data_transmission_send"
        super(MQConsumerTask, self).__init__(name, url, "", queue_name, routing_key)
        self.kafka_config = config.get("kafka")
        self.kafka_host = self.kafka_config.get("host", "127.0.0.1")
        self.kafka_port = self.kafka_config.get("port", 9092)
        self.kafka_host = "{}:{}".format(self.kafka_host, self.kafka_port)
        self.alarm_topic = config.get("alarm_topic", "alarm-data")
        # 接收端保存数据文件的路径
        self.receive_file_path = config.get("save_receive_data", "/tmp/receive_file")
        # 接收端保存升级包的文件路径
        self.receive_package_path = config.get("receive_update_package", "/tmp/receive_package")
        # 接收端，ES的配置信息
        self.elastic_query_obj = ElasticsearchHelper(config.get("elastic"), config.get("db_url"))
        # 发送端的ES配置信息
        self.dst_es = config.get("dst_es")
        # 存放拆分文件的临时变量
        self.split_file_number = dict()
        self.kafka_obj = KafkaHelper(config.get("db_url"))
        self.mq_url = config.get("mq_url")

    def do(self, body):
        """ the main handle.

        从rabbitmq中接收告警数据和文件数据并发送到本级的kafka中.

        :param body: mq message
        """
        try:
            if isinstance(body, bytes):
                body = body.decode('utf-8')
            json_data = json.loads(body)
            extra_data = json_data.get("data")
            data_type = extra_data.get("type")
            if data_type == "alarm":
                print("------------ receive alarm data -----------------------")
                task_id = json_data.get("task_id")
                data = json_data.get("msgdata")
                self.kafka_obj.send_to_kafka(task_id=task_id, data=data, topic=self.alarm_topic, hosts=self.kafka_host,
                                             type_of="alarm", source="receive")
            # 保存文件数据
            elif data_type == "file":
                print("------------ receive file data -----------------------")
                es_data = extra_data.get("transmission_data")
                temp_data = copy.deepcopy(json_data)
                temp_data.get("data").pop("transmission_data")
                file_name = extra_data.get("current_file_name")
                task_id = json_data.get("task_id")
                split_file_name = file_name.split("_")
                file_path = os.path.join(self.receive_file_path, split_file_name[0])
                send_params = dict()
                send_params.setdefault("file_path", file_path)
                send_params.setdefault("current_file_name", file_name)
                # 保存文件数据
                es_data = json_loads(es_data)
                FILEOPERATOR.save_file(es_data, file_name, file_path)
                # 将文件内容录入到ES中
                self.elastic_query_obj.insert_into_es(task_id, send_params=send_params, typeof="file",
                                                      data=es_data, es_handler=self.dst_es, source="receive")
            # 保存升级包
            elif data_type == "package":
                print("------------ receive package data -----------------------")
                file_content = json_data.get("data")
                file_name = json_data.get("file_name")
                file_number = json_data.get("file_number")
                FILEOPERATOR.save_file_bytes(file_content, file_name, self.receive_package_path)
                if "file_number" in json_data:
                    now_number = self.split_file_number.get(file_name, 0)
                    self.split_file_number.setdefault(file_name, now_number + 1)
                    if file_number == now_number + 1:
                        LOG_WARNING.info(u"升级包传输完成")
                        # 清空缓存
                        self.split_file_number.pop(file_name)
                else:
                    LOG_WARNING.info(u"升级包传输完成")
            elif data_type == "update":
                task_id = json_data.get("task_id")
                update_records = json_data.get("msgdata", None)
                if update_records:
                    MYSQLHELPER.insert_update(task_id, "update", update_records, "receive")
                # 给monitor_server发送升级策略
                try:
                    case_update = extra_data.get("case")
                    for update_record in update_records:
                        soft_state = update_record.get("soft_state")
                        if int(soft_state) == 20:
                            server_name = update_record.get("server_name")
                            version = update_record.get("version")
                            for each in case_update:
                                server_name_case = each.get("server_name")
                                version_case = each.get("version")
                                if server_name == server_name_case and version == version_case:
                                    temp_update = [each]
                                    if not isinstance(temp_update, str):
                                        temp_update = json_dumps(temp_update)
                                    MQClient.send_message(url=self.mq_url, exchange_name="", routing_key="update_server", message=temp_update)
                except Exception as ex:
                    LOG_WARNING.error(u"mq消息发送失败，原因为:{}".format(str(ex)))
            else:
                LOG_WARNING.error(u"接收rabbitmq消息时，数据的格式不是预期要处理的格式，丢弃该数据。")
        except Exception as ex:
            LOG_WARNING.error(u"在处理rabbitmq消息时发生错误，错误原因:{}".format(str(ex)))


class ReceiveNotice(MQProcess):
    def __init__(self, name, config):
        mq_url = config.get("mq_url")
        queue_name = config.get("notice_queue", "notice_queue")
        routing_key = queue_name
        super(ReceiveNotice, self).__init__(name, mq_url, "", queue_name, routing_key)
        self.check_except = CheckExcept(config)

    def do(self, body):
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        json_data = json_loads(body)
        if not json_data:
            LOG.info(u"反馈的数据格式不正确，不处理。")
            return
        print(json_data)
        if not isinstance(json_data, list):
            json_data = [json_data]
        for each in json_data:
            if isinstance(each, dict):
                task_id = each.get("task_id")
                state = each.get("state")
                self.check_except.notice_message(task_id, state)


def get_env(config):
    package_path = None
    env_path = None
    operate_system = platform.system().lower()
    if operate_system == "linux":
        env_args = config.get("linux_os")
    else:
        env_args = config.get("windows_os")
    if env_args:
        package_path = env_args.get("package_path")
        env_path = env_args.get("env_path")
    zookeeper = config.get("zk")
    return package_path, env_path, zookeeper


def remove_log_file():
    global _ENV_ARGS
    logging_name = {
        "error_name": "",
        "info_name": "",
        "access_name": ""
    }
    possible_topdir = os.path.normpath(os.path.join(os.path.abspath(__file__),
                                                    os.pardir,
                                                    os.pardir
                                                    ))
    cp = configparser.ConfigParser()
    file_path = os.path.join(possible_topdir, 'etc', 'logging.conf')
    cp.read(file_path)
    cp.sections()

    logging_name["error_name"] = ast.literal_eval(cp._sections["handler_file"]['args'])[0]

    logging_name["info_name"] = ast.literal_eval(cp._sections["handler_log_file"]['args'])[0]
    logging_name["access_name"] = ast.literal_eval(cp._sections["handler_access_file"]['args'])[0]
    env_path = _ENV_ARGS[1]
    for value in logging_name.values():
        if os.path.exists(env_path + value):
            os.remove(env_path + value)
            LOG.info("{} has removed".format(value))
        else:
            LOG.info("{} file is not exist".format(value))


def work_func(config):
    """ the main server function.

    main task added function, for this server,rabbit-mq receiver and handler,
    inner processing queue monitor, send message to logstash.

    :param config: database connection info ,rabbit-mq connection info,
        logstash connection info is included
    """

    LOG.info('start work func')
    config['monitor_exchange'] = 'data_transmission'

    global CONFIG, JPYPEHELPER, MYSQLHELPER
    CONFIG = config
    db_url = config.get("db_url")
    JPYPEHELPER = JpypeHelper(db_url)
    MYSQLHELPER = MysqlHelper(db_url)

    global _MQ_CONSUMER

    # 初始化java反馈通知
    mq = config.get("mq")
    notice_queue_name = config.get("notice_queue", "notice_queue")
    JPYPEHELPER.init_notice(mq, notice_queue_name)

    # 初始化java发送接口
    source_queue = config.get("source_queue", "data_transmission_source")
    JPYPEHELPER.init_send(mq, queue_name=source_queue)

    # 初始化java接收接口
    java_receive_queue = config.get("send_queue", "data_transmission_send")
    java_send_queue = config.get("receive_queue", "data_transmission_receive")
    JPYPEHELPER.receive_notice(mq, java_receive_queue, java_send_queue)

    # 先检查之前是否有异常情况，需要再次发送数据
    check_obj = CheckExcept(config)
    check_obj.check()

    # 本级kafka 告警数据消费（发送端）
    _send_alarm = AlarmDataFromKafka("alarm_data_consumer", config)
    # 本级ES 聚合、统计数据落地成文件并发送到rabbitmq队列中（发送端）
    _send_file = SendFileData("file_data_save", config)
    # 从rabbitmq接收升级信息，下载升级包，一并下发到下级节点（发送端）
    _send_version = SendVersionData("send_version_data", config)
    # 接收rabbitmq 本地接收数据（接收端）
    _receive_mq_message = MQConsumerTask("receive_mq_message", config)
    # 接收反馈通知（发送端）
    _receive_notice = ReceiveNotice("receive_notice", config)

    ProcessManage().add_task(_send_alarm)
    ProcessManage().add_task(_send_file)
    ProcessManage().add_task(_send_version)
    ProcessManage().add_task(_receive_mq_message)
    ProcessManage().add_task(_receive_notice)

    ProcessManage().start(_send_alarm.name())
    ProcessManage().start(_send_file.name())
    ProcessManage().start(_send_version.name())
    ProcessManage().start(_receive_mq_message.name())
    ProcessManage().start(_receive_notice.name())


def main_func(config):
    """before main function do something.

    add main sever handle, add tasks.

    :param config: transport config parameters ,database connection info ,
    rabbit-mq connection info, logstash connection info included
    """
    # do framework things
    global _ENV_ARGS
    _ENV_ARGS = get_env(config)

    LOG.info('manage start ok')
    LOG.info('config -------- %s' % config)
    possible_topdir = os.path.normpath(os.path.join(os.path.abspath(__file__),
                                                    os.pardir,
                                                    os.pardir))

    deploy_file = open(os.path.join(possible_topdir, 'etc', 'deploy.conf'))
    deploy_dict = json.load(deploy_file)
    global HOST_IP
    global HOST_PORT
    HOST_IP = deploy_dict["manage_rest"]["host"]
    HOST_PORT = deploy_dict["manage_rest"]["port"]
    # do work things
    work_func(config)


def run():
    # run_applications()
    Server(main_func, heartbeat=MyHeartBeatTask, manager=ManagerImp)
    LOG.info('start work ok -----')


if __name__ == '__main__':
    # run_applications()
    Server(main_func, heartbeat=MyHeartBeatTask, manager=ManagerImp)
    LOG.info('start work ok -----')
