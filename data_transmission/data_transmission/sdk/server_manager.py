""" server manage process package.

all server manage process class.

Manager is implement manage http interface
TaskManage manage all tasks
Task one task implement
MQTask mq consume task
HttpTask is implement http thread
HeartBeatTask is implement heart beat task
Server is implement server instance

"""
import os
import json
import argparse
import threading
import time
import multiprocessing
import kafka
import schedule
from eventlet import sleep
from kafka.errors import NoBrokersAvailable
from oslo_log import log
from ..sdk import zk_help
from ..sdk.common import start_thread, Singleton,start_process,stop_process
from ..sdk.common.exception import MyError
from ..sdk.http.run_applications import run_applications
from ..sdk.mq import MQConsumerService, ExchangeParameters, QueueParameters, \
    ChannelParameters
from data_transmission.application.load_config import config_info

LOG = log.getLogger('log')
LOG_WARNING = log.getLogger('warning')
SERVER_PID = multiprocessing.Queue()
# mq接收消息与mq类是两个进程 杀掉一个任务需要杀掉两个进程，进程号保存在这里
MQ_SERVER_PID = multiprocessing.Queue()
PPID_PID_DICT_OR_LIST = multiprocessing.Queue()


class Manager(object):
    """manage http class.

    所属单元: 消息获取解析单元

    implement manage url func
    get : name version
    get /info: cpu memory info
    get /manage/start
    get /manage/stop
    get /manage/restart

    """

    the_instance = None

    def __init__(self):
        """init func.

        set _instance is this

        """
        Manager.the_instance = self
        self.status = 'running'
        self._version = '0.0.1'

    def tests(self):
        """test func.

        url is /tests

        """
        return 'manager test return'

    def info(self):
        """get service info."""
        result = dict()
        result['status'] = self.status
        return result

    def start(self,body):
        """start service."""
        return 'start'

    def stop(self,body):
        """stop service."""
        return 'stop'

    def restart(self):
        """restart service."""
        return 'restart'

    def update(self):
        """update this service."""
        return 'update'

    def version(self):
        """get this service version."""
        return self._version

    def application_info(self):
        """inner func.

        get the work application info
        """
        pass


class TaskManage(metaclass=Singleton):
    """task manage implement class, is a singleton class.

    Attributes:
        _tasks: all tasks info.
    """

    def __init__(self):
        """init func."""
        self._tasks = dict()

    def add_task(self, task):
        """add task.

        :param task: task instance

        """
        self._tasks[task.name()] = task

    def start(self, name):
        """start task by name.

        :param name: task name

        """
        if name in self._tasks:
            self._tasks[name].start()

    def stop(self, name):
        """stop task by name.

        :param name: task name

        """
        if name in self._tasks:
            self._tasks[name].stop()

    def start_all(self):
        """start all tasks in task manges."""
        for k, v in self._tasks.items():
            v.start()

    def stop_all(self):
        """stop all tasks in task manges."""
        for k, v in self._tasks.items():
            v.stop()

    def join_all(self):
        """join all tasks in task manage."""
        for k, v in self._tasks.items():
            v.join()

    def get_status(self):
        """get current status."""
        pass

    def current(self):
        """get current running task name.

        :return str: running task name
        """
        return threading.current_thread().getName()


class Task(object):
    """implement task option class.

    Attributes:
        _name: task name, unique.
        _func: task thread function.
        _thread: task thread.
        _interval: schedule seconds.
        _running: run state.
    """

    def __init__(self, name, func=None, interval=None, *args, **kwargs):
        """init func.

        :param str name: task name, unique
        :param callback func: func, if none is set self.do
        :param int interval: schedule seconds

        """
        # threading.Thread.__init__(self)
        self._name = name
        if func:
            self._func = func
        else:
            self._func = self.do
        self._thread = None
        self._interval = interval
        self._running = True
        self._args = args
        self._kwargs = kwargs

    def name(self):
        """get task name.

        :return str: task name

        """
        return self._name

    def run(self):
        """task thread run func."""
        if self._interval:
            wait_seconds = 0
            while self._running:
                if (wait_seconds % self._interval) == 0:
                    self._func(*self._args, **self._kwargs)
                sleep(1)
                wait_seconds += 1
        else:
            if self._running and self._func:
                self._func(*self._args, **self._kwargs)

    def do(self, *args, **kwargs):
        """default schedule do func, you can rewrite it."""
        pass

    def stop(self):
        """stop task."""
        self._running = False

    def start(self):
        """start task."""

        self._thread = start_thread(self._name, self.run)
        self._running = True

    def join(self):
        """join task."""
        if self._thread:
            self._thread.join()


class MQTask(Task):
    """MQ consume task class.

    所属单元: 数据获取提取单元

    """

    def __init__(self, name, url, exchange_name=None, queue_name=None, routing_key=None):
        """init func.

        :param str name: task name
        :param str url: mq server connect url
        :param str exchange_name: mq exchange name
        :param str queue_name: mq queue name
        :param str routing_key: the routing key for mq bind exchange and queue
        """
        super(MQTask, self).__init__(name)
        self._mq_consumer = MQConsumerService(url,
                                              exchange=ExchangeParameters(exchange_name, False),
                                              queue=QueueParameters(queue_name, False),
                                              channel_params=ChannelParameters(1),
                                              routing_key=routing_key,
                                              proc=self.do)

    def run(self):
        """task thread run func."""
        self._mq_consumer.start_consumer()

    def do(self, body):
        """schedule do func.

        receive mq message, process message func

        :param body: The message body; empty string if no body
        :type body: str or unicode
        """
        pass

    def stop(self):
        """stop mq consume."""
        self._mq_consumer.stop_consumer()


class ProcessManage(metaclass=Singleton):
    """task manage implement class, is a singleton class.

    Attributes:
        _tasks: all tasks info.
    """

    def __init__(self):
        """init func."""
        self._tasks = dict()

    def add_task(self, task):
        """add task.

        :param task: task instance

        """
        self._tasks[task.name()] = task

    def start(self, name):
        """start task by name.

        :param name: task name

        """
        if name in self._tasks:
            temp_name = self._tasks[name].start()
            self._tasks[temp_name] = self._tasks.pop(name)

    def stop(self, pid_list):
        """stop task by name.

        :param name: task name

        """
        for pid in pid_list:
            if pid in self._tasks.keys():
                stop_process(pid)
                self._tasks[pid].get_process().join()

                self._tasks.pop(pid)

    def get_status(self):
        """get current status."""
        pass

    def get_task(self):
        return self._tasks


class Process(object):
    """implement task option class.

    Attributes:
        _name: task name, unique.
        _func: task thread function.
        _process: task process.
        _interval: schedule seconds.
        _running: run state.
    """

    def __init__(self, name, func=None, interval=None, *args, **kwargs):
        """init func.

        :param str name: task name, unique
        :param callback func: func, if none is set self.do
        :param int interval: schedule seconds

        """
        # threading.Thread.__init__(self)
        self._name = name
        if func:
            self._func = func
        else:
            self._func = self.do

        self._process = None
        self._interval = interval
        self._running = True
        self._args = args
        self._kwargs = kwargs
        self._mq_pid =None
        self.parent_pid = os.getpid()

    def name(self):
        """get task name.

        :return str: task name

        """
        return self._name

    def run(self):
        """task thread run func."""
        if self._interval:
            wait_seconds = 0
            while self._running:
                if (wait_seconds % self._interval) == 0:
                    self._func(*self._args, **self._kwargs)
                sleep(1)
                wait_seconds += 1
        else:
            if self._running and self._func:
                self._func(*self._args, **self._kwargs)

    def do(self, *args, **kwargs):
        """default schedule do func, you can rewrite it."""
        pass

    def stop(self):
        """stop task."""
        self._running = False

    def start(self):
        """start task."""

        self._process = start_process(self._name, self.run)
        self._name = self._process.pid
        self._running = True
        return self._name

    def join(self):
        """join task."""
        if self._process:
            self._process.join()

    def get_process(self):
        return self._process

    def check_parent_pid(self):
        """ Check For the existence of a unix pid. """
        try:
            os.kill(self.parent_pid, 0)
        except OSError:
            exit("主进程退出 ,{}退出".format(os.getpid()))
            return False
        else:
            return True


class MQProcess(Process):
    """MQ consume task class.

    所属单元: 数据获取提取单元

    """

    def __init__(self, name, url, exchange_name=None, queue_name=None, routing_key=None):
        """init func.

        :param str name: task name
        :param str url: mq server connect url
        :param str exchange_name: mq exchange name
        :param str queue_name: mq queue name
        :param str routing_key: the routing key for mq bind exchange and queue
        """
        super(MQProcess, self).__init__(name)
        self._mq_consumer = MQConsumerService(url,
                                              exchange=ExchangeParameters(exchange_name, False),
                                              queue=QueueParameters(queue_name, False),
                                              channel_params=ChannelParameters(1),
                                              routing_key=routing_key,
                                              proc=self.do)

    def run(self):
        """task thread run func."""

        self._mq_consumer.start_consumer()

    def do(self, body):
        """schedule do func.

        receive mq message, process message func

        :param body: The message body; empty string if no body
        :type body: str or unicode
        """
        pass

    def stop(self):
        """stop mq consume."""
        self._mq_consumer.stop_consumer()

    def start(self):
        """start task."""

        self._process = start_process(self._name, self.run)

        self._name =self._process.pid

        self._running = True
        return self._name


class KafkaTask(Task):
    def __init__(self, name, hosts, topic, group_id, func=None):
        super(KafkaTask, self).__init__(name, func=self.consume_kafka)
        self._hosts = hosts
        self._topic = topic
        self._group_id = group_id
        if func:
            self._consume_func = func
        else:
            self._consume_func = self.do
        self._consumer = None
        self._producer = None

    def consume_kafka(self):
        while not self._consumer:
            try:
                self._consumer = kafka.KafkaConsumer(
                    self._topic,
                    bootstrap_servers=self._hosts,
                    group_id=self._group_id,
                )
            except NoBrokersAvailable as ex:
                LOG_WARNING.error('kafka connect error:{}'.format(str(ex)))
                time.sleep(3)
        LOG.info('connect to kakfa host:{} topic:{} group_id:{}'.format(self._hosts, self._topic, self._group_id))

        for message in self._consumer:
            try:
                self._consume_func(message=message)
            except Exception as ex:
                LOG_WARNING.error('kafka message consume ex:{}'.format(str(ex)))
                raise MyError(ex)

    def produce_kafka(self, topic, data):
        while not self._producer:
            print("connect kafka")
            self._producer = kafka.KafkaProducer(bootstrap_servers=self._hosts)
        try:
            self._producer.send(topic=topic, value=data)
            return True
        except:
            LOG_WARNING.error(u"向Kafka的topic为{}发送数据失败".format(topic))
        return False


class HttpTask(Task):
    """http thread process class."""

    def __init__(self):
        """init func."""
        super(HttpTask, self).__init__('http_task')

    def do(self, *args, **kwargs):
        """start http service thread."""
        run_applications()


class HeartBeatTask(Task):
    """heart beat task implement class.

    Attributes:
        _monitor: mq queue info.
        _version: version info.
        _config: system config info.

    """

    def __init__(self, config):
        """init func.

        :param config: system config info.

        """

        super(HeartBeatTask, self).__init__('heartbeat_task', interval=5)
        self._monitor = ''
        self._version = 'xxx'
        self._config = config

    def do(self, *args, **kwargs):
        """schedule heart beat process func."""
        print('ori heart beat')


class Server(object):
    """the application implement class."""

    def __init__(self, application, heartbeat=HeartBeatTask, manager=Manager):
        """init func.

        :param callback application: application function
        :param heartbeat: implement heart beat class
        :param manager: implement mange http func class

        """
        try:
            self.config = None
            self.parse_args()

            self._manager = manager()

            TaskManage().add_task(heartbeat(config=self.config))
            TaskManage().add_task(HttpTask())
            TaskManage().start_all()
            start_thread('run_schedule', self.schedule_run)
            self._app = application(self.config)
        except MyError as ex:
            raise ex
        except Exception as ex:
            LOG_WARNING.error('server start ex is ', ex)
            raise MyError(ex)

    def parse_args(self):
        """parse args."""
        parser = argparse.ArgumentParser(description="server")
        parser.add_argument('-z', '--zookeeper', default='127.0.0.1:2181')
        parser.add_argument('-n', '--parent-node', default='/task_server/master')
        parser.add_argument("-e", "--elasticserach", default=None)
        args = parser.parse_args()
        self.get_config(args)

    def get_config(self, args):
        """from zookeeper server get common config.

        :param dict args: application args

        """

        zk = zk_help.ZkHelp(hosts=args.zookeeper)
        while not zk.m_isActive:
            try:
                zk.start()
            except Exception as ex:
                LOG_WARNING.error('zk start ex: ', ex, ' 5 seconds try again')
                time.sleep(3)

        self.config = zk.get_node_data(args.parent_node)
        while not self.config:
            LOG.info('zk get config is none 3 seconds try again')
            time.sleep(3)
            self.config = zk.get_node_data(args.parent_node)

        # 合并本地配置文件信息
        self.config = dict(self.config, **config_info)
        if args.elasticserach:
            self.config["dst_es"] = args.elasticserach

        # get db url
        if 'db' in self.config:
            self.config['db_url'] = 'mysql+mysqlconnector://' + self.config['db']['user'] + ':' \
                                    + self.config['db']['password'] + '@' \
                                    + self.config['db']['host'] + ':' + self.config['db']['port'] \
                                    + '/' + self.config['db']['database'] \
                                    + '?charset=' + self.config['db']['charset']

        # get mq url
        if 'mq' in self.config:
            # "amqp://admin:admin@192.168.0.131:5672"
            self.config['mq_url'] = \
                'amqp://%(user)s:%(password)s@%(host)s:%(port)s' % self.config['mq']

        self.config['zk'] = args.zookeeper
        self.write_deploy()
        zk.stop_zk()

    def schedule_run(self):
        """schedule process func."""
        while True:
            schedule.run_pending()
            sleep(1)

    def start(self):
        """start all tasks and join them."""
        TaskManage().start_all()
        TaskManage().join_all()

    def write_deploy(self):
        '''write ip port to deploy.conf'''
        local_ip = '0.0.0.0'
        port = 5566
        filepath = os.path.abspath(__file__)
        server_name = filepath.split("/")[-3]
        for server_name_config, ip_port in self.config.items():
            if server_name_config == server_name:
                local_ip = self.config[server_name_config]['ip']
                port = self.config[server_name_config]['port'].split(',')[0]
                break
        content = {
                  "manage_rest": {
                    "host": "0.0.0.0",
                    "port": "8008",
                    "app_name": "main",
                    "threads": 100,
                    "config_file_name": "manage.ini"
                  }
                }
        content["manage_rest"]["host"] = local_ip
        content["manage_rest"]["port"] = port

        possible_topdir = os.path.normpath(os.path.join(os.path.abspath(__file__),
                                                        os.pardir,
                                                        os.pardir
                                                        ))
        deploy_file = open(os.path.join(possible_topdir, 'etc', 'deploy.conf'), 'w')
        json.dump(content, deploy_file)
        deploy_file.close()
