#!/usr/env/bin python
# -*-encoding:utf-8 -*-
import threading
import time
import logging
import json
import os
import sys
import sqlite3
import uuid
import multiprocessing

from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings
from scrapy.crawler import signals
from twisted.internet import reactor
from bottle import run, request, HTTPResponse
from bottle import Bottle

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('..')
path = sys.argv[0]
os.chdir(os.path.dirname(path))

from crawl_of_pushtime_second_version.spiders.mySpider import MySpider
from load_config import http_host, http_port, FileStoredPath
from date2cron import cron_to_date


# 计划表本地的sqlite3数据库
plan_state_db_path = os.path.join(FileStoredPath, "PlanState.db3")
# 规则文件本地化的目录
local_rule_file_path = os.path.join(FileStoredPath, "rule_file")
# 计划表
SPIDER_PLAN = "spider_plan"
# 统计计划表
SPIDER_COUNT = "spider_count"
# 管理爬虫进程(轮询)
SPIDER_PROCESS = dict()
# 立即执行的进程管理
SPIDER_PROCESS_NOW = dict()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='GateWay.log',
                    filemode='w')
# 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)10s: %(filename)-12s %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


# json字符串转json
def json_loads(msg):
    try:
        if msg:
            msg = json.loads(msg)
        return msg
    except Exception as ex:
        logging.error(u"格式化post参数出错，错误原因为:{}".format(str(ex)))
        logging.error(u"错误的参数:{}".format(msg))
    return None


class SqliteHelper(object):
    @staticmethod
    def sqlite_handler():
        try:
            db_path = os.path.dirname(plan_state_db_path)
            if not os.path.isdir(db_path):
                os.makedirs(db_path)
            handler = sqlite3.connect(plan_state_db_path, timeout=60)
            return handler
        except Exception as ex:
            logging.error(u"连接计划状态数据库错误,错误原因为:{}".format(str(ex)))
        return None

    @staticmethod
    def sqlite_close(handler):
        try:
            handler.close()
            time.sleep(0.1)
            return True
        except Exception as ex:
            logging.error(u"关闭sqlite数据库发生错误,错误原因为:{}".format(str(ex)))
        return False

    def sqlite_query(self, sql):
        res = None
        try:
            handler = self.sqlite_handler()
            if handler:
                res = handler.execute(sql)

        except Exception as ex:
            logging.error(u"查询sqlite数据库发生异常,异常原因为:{}".format(str(ex)))
            logging.error(u"错误的sql语句为:{}".format(sql))
        return res

    def sqlite_update_delete_insert(self, sql):
        res = False
        try:
            handler = self.sqlite_handler()
            if handler:
                handler.execute(sql)
                handler.commit()
                res = True
        except Exception as ex:
            logging.info(u"操作sqlite数据库发生异常, 异常原因为:{}".format(str(ex)))
            logging.error(u"错误的sql语句为:{}".format(sql))
        return res

    def sqlite_create_table(self):
        try:
            sql = "create table if not exists {}(id INTEGER default 1, statistics INTEGER);".format(SPIDER_COUNT)
            self.sqlite_update_delete_insert(sql)
            self.init_spider_count()
            sql = "create table if not exists {}(id INTEGER primary key autoincrement, " \
                  "rule_id int, Cron varchar(32), NextFireTime timestamp, rule_name varchar(255), urls TEXT, plan_id varchar(64), " \
                  "is_delete int, is_stop int, spider_status varchar(255), description TEXT);".format(SPIDER_PLAN)
            self.sqlite_update_delete_insert(sql)
        except Exception as ex:
            logging.info(u"sqlite创建表时发生异常, 异常原因为:{}".format(str(ex)))
            logging.error(u"错误的sql语句为:{}".format(sql))

    def init_spider_count(self):
        sql = "select id from {};".format(SPIDER_COUNT)
        res = self.sqlite_query(sql).fetchone()
        insert_sql = "insert into {} (id) values (1);".format(SPIDER_COUNT)
        if res:
            init_id = res[0]
            if not init_id:
                self.sqlite_update_delete_insert(insert_sql)
        else:
            self.sqlite_update_delete_insert(insert_sql)


class ExecuteSpiderByProcess(object):
    def __init__(self):
        self.sqlite_helper = SqliteHelper()

    @staticmethod
    def get_rule_file_path(rule_id):
        if isinstance(rule_id, int):
            rule_id = str(rule_id)
        rule_path = os.path.join(local_rule_file_path, rule_id)
        return rule_path

    def read_rule_file(self, rule_path):
        content = None
        if os.path.isfile(rule_path):
            with open(rule_path, 'r') as files:
                content = files.read()
        else:
            logging.error(u"规则文件不存在,检查文件路径:{}".format(rule_path))
        return content

    def format_spider_kwargs(self, row):
        spider_kwargs = dict()
        rule_path = self.get_rule_file_path(rule_id=row[1])
        rule_file_path = os.path.join(rule_path, row[4] + ".xml")
        urls_json_string = row[5]
        urls_json = json_loads(urls_json_string)
        next_fire_time = row[3]
        rule_name = row[4]
        spider_kwargs.setdefault("next_time", next_fire_time)
        spider_kwargs.setdefault("FileContent", self.read_rule_file(rule_file_path))
        spider_kwargs.setdefault("isRss", 0)
        spider_kwargs.setdefault("max_depth", 0)
        spider_kwargs.setdefault("PlanID", row[6])
        spider_kwargs.setdefault("PlanType", 140)
        spider_kwargs.setdefault("Url", urls_json)
        spider_kwargs.setdefault("task_id", str(row[1]))
        spider_kwargs.setdefault("FileName", rule_name)
        # 当store_type为True时.需要store_dir字段
        spider_kwargs.setdefault("store_type", True)
        spider_kwargs.setdefault("PlanType", 140)
        spider_kwargs.setdefault("selectType", "1"),
        spider_kwargs.setdefault("PlanName", rule_name)
        spider_kwargs.setdefault("store_dir", row[6])
        # print json.dumps(spider_kwargs)
        return spider_kwargs

    def check_plan(self, rule_id):
        spider_kwargs = dict()
        # 先查询计划表的任务信息
        query_sql = "select * from {} where rule_id={} and is_delete=0;".format(SPIDER_PLAN, rule_id)
        row = self.sqlite_helper.sqlite_query(query_sql).fetchone()
        if row:
            spider_kwargs = self.format_spider_kwargs(row)
        else:
            logging.info(u"计划可能已经被删除,停止计划运行")
        return spider_kwargs

    def execute_spider(self, kwargs):
        global SPIDER_PROCESS
        spider_task_id = kwargs.get("task_id")
        # 先判断当前计划是否在执行状态
        process_pid = SPIDER_PROCESS.get(spider_task_id, None)
        if process_pid:
            logging.info(u"计划执行中或等待中,不可再次启动计划")
            return False
        spider_kwargs = dict()
        spider_kwargs["category"] = kwargs
        process = multiprocessing.Process(target=self.start_spider, args=(spider_kwargs, ))
        process.start()
        # 进程启动以后才有返回值
        pid = process.pid
        SPIDER_PROCESS[str(spider_task_id)] = pid
        return True

    def start_spider_now(self, kwargs):
        global SPIDER_PROCESS_NOW
        spider_task_id = kwargs.get("task_id")
        # 先判断当前计划是否在执行状态
        process_pid = SPIDER_PROCESS_NOW.get(spider_task_id, None)
        if process_pid:
            logging.info(u"计划执行中或等待中,不可再次启动计划")
            return False
        spider_kwargs = dict()
        spider_kwargs["category"] = kwargs
        process = multiprocessing.Process(target=self.start_spider_now_helper, args=(spider_kwargs, ))
        process.start()
        # 进程启动以后才有返回值
        pid = process.pid
        SPIDER_PROCESS_NOW[str(spider_task_id)] = pid
        return True

    def start_spider_now_helper(self, kwargs):
        self.execute_spider_callback(**kwargs)

    # 更新下次执行的时间
    def update_next_time(self, rule_id):
        query_sql = "select Cron from {} where rule_id={};".format(SPIDER_PLAN, rule_id)
        row = self.sqlite_helper.sqlite_query(query_sql).fetchone()
        next_time = None
        if row:
            cron = row[0]
            next_time = cron_to_date(cron)
            update_sql = "update {} set NextFireTime='{}' where rule_id={};".format(SPIDER_PLAN, next_time, rule_id)
            self.sqlite_helper.sqlite_update_delete_insert(update_sql)
        return next_time

    def update_spider_state(self, state, rule_id):
        update_sql = "update {} set spider_status='{}', is_stop=0 where rule_id={};".format(SPIDER_PLAN, state, rule_id)
        self.sqlite_helper.sqlite_update_delete_insert(update_sql)

    def start_spider(self, kwargs):
        global SPIDER_PROCESS
        rule_id = kwargs["category"].get("task_id")
        # 执行爬虫
        self.execute_spider_callback(**kwargs)
        # TODO 验证爬虫是否是顺序执行
        self.update_next_time(rule_id)
        self.update_spider_state(state=u"等待下次执行", rule_id=rule_id)
        # 清除进程内存信息
        SPIDER_PROCESS.pop(str(rule_id))

    def execute_spider_callback(self, **kwargs):
        spider = MySpider(category=kwargs['category'])
        settings = get_project_settings()
        crawler = Crawler(spider, settings=settings)
        crawler.signals.connect(self.spider_close, signal=signals.spider_closed)
        d = crawler.crawl(spider, category=kwargs['category'])
        d.addBoth(lambda _: reactor.stop())
        reactor.run()

    def spider_close(self):
        # 爬虫结束回调此方法
        print "----------- spider end ------------"
        logging.info(u"本次爬取任务以完成")

    def stop_spider(self, rule_id, param):
        # 返回状态信息
        global SPIDER_PROCESS, SPIDER_PROCESS_NOW
        # param 为1的时候，停止立刻执行的计划，为0的时候，停止轮询的计划
        try:
            rule_id = str(rule_id)
            # 将爬虫进程停止,kill进程
            if param == 1:
                process_pid = SPIDER_PROCESS_NOW.get(rule_id, None)
            else:
                process_pid = SPIDER_PROCESS.get(rule_id, None)
            if process_pid:
                command = "kill -9 {}".format(process_pid)
                self.kill_process(command)
                if param == 1:
                    SPIDER_PROCESS_NOW.pop(rule_id)
                else:
                    SPIDER_PROCESS.pop(rule_id)
                status = u"停止计划成功"
                flag = True
            else:
                logging.info(u"rule_id为{}的计划未在执行或没有该计划,不操作".format(rule_id))
                status = u"rule_id为{}的计划未在执行或没有该计划,不操作".format(rule_id)
                flag = True
        except Exception as ex:
            status = u"停止当前计划进程发生异常,异常原因为:{}".format(str(ex))
            logging.error(u"停止当前计划进程发生异常,异常原因为:{}".format(str(ex)))
            flag = False
        return flag, status

    @staticmethod
    def kill_process(command):
        logging.info(u"执行的kill命令为:{}".format(command))
        os.popen(command)


# 接收web发来的http消息，并对消息进行处理
class RequestHandlers(object):
    def __init__(self, local_ip=None, local_port=-1, db_folder=None):
        self.rule_app = Bottle()
        self.ip = local_ip
        self.port = local_port
        self.db_folder = db_folder
        self.thread_list = dict()
        self.fileContentIsFilePath = False
        self.sqlite_helper = SqliteHelper()
        self.execute_spider = ExecuteSpiderByProcess()

        # 增加计划
        @self.rule_app.route('/rules/add', method='POST')
        def add_plan():
            response = dict()
            # 默认添加计划为失败状态
            add_plan_flag = 1
            rule_id = None
            try:
                rule_json = request.POST["rule_json"]
                rule_json = json.loads(rule_json, encoding="utf8")
                rule_cron = request.POST["rule_cron"]
                rule_name = rule_json.get("rule_name")
                rule_file = request.POST["rule_file"]
                count_sql = "select * from {};".format(SPIDER_COUNT)
                query_result = self.sqlite_helper.sqlite_query(count_sql)
                row = query_result.fetchone()
                # 查找出当前已有
                if row:
                    cell = row[1]
                    if not cell:
                        rule_id = 0
                    else:
                        rule_id = cell
                else:
                    rule_id = 0
                rule_id += 1
                # 本地化规则文件
                try:
                    rule_path = self.get_rule_file_path(rule_id)
                    if not os.path.isdir(rule_path):
                        os.makedirs(rule_path)
                    rule_file.save(os.path.join(rule_path, rule_name + ".xml"), overwrite=True)
                    # self.write_rule_file(rule_name, rule_path, rule_file)
                except Exception as ex:
                    error_message = u"规则文件本地化时发生异常,异常原因为:{}".format(str(ex))
                    response.setdefault("result", add_plan_flag)
                    response.setdefault("detail", error_message)
                    response.setdefault("rule_id", rule_id)
                    return HTTPResponse(status=200, body=response)
                try:
                    next_time = cron_to_date(rule_cron)
                except Exception as ex:
                    logging.error(u"Cron表达式转化失败,此次计划不进行添加, 错误原因为:{}".format(str(ex)))
                    response.setdefault("result", add_plan_flag)
                    add_plan_detail = u"计划创建失败,Cron表达式转化失败"
                    response.setdefault("detail", add_plan_detail)
                    response.setdefault("rule_id", rule_id)
                    return HTTPResponse(status=200, body=response)
                collect_url_json = rule_json.get("urls", None)
                collect_url_json_string = json.dumps(collect_url_json)
                plan_id = str(uuid.uuid4())
                add_plan_sql = "insert into {} (rule_id, Cron, NextFireTime, rule_name, urls, plan_id, " \
                               "is_delete, is_stop, spider_status, description) " \
                               "values ({}, '{}', '{}', '{}', '{}','{}', {}, {}, '{}', '{}');"
                add_plan_sql = add_plan_sql.format(SPIDER_PLAN, rule_id, rule_cron, next_time, rule_name,
                                                   collect_url_json_string, plan_id, 0, 0, u"等待中", "")
                flag = self.sqlite_helper.sqlite_update_delete_insert(add_plan_sql)
                if flag:
                    update_count_sql = "update {} set statistics={};".format(SPIDER_COUNT, rule_id)
                    self.sqlite_helper.sqlite_update_delete_insert(update_count_sql)
                    # 返回http数据
                    add_plan_flag = 0
                    add_plan_detail = u"计划创建成功"
                else:
                    add_plan_detail = u"数据格式有问题,请检查数据格式.数据为:{}".format(request.POST.items())
            except Exception as ex:
                logging.error(u"添加计划时发生异常,异常原因为:{}".format(str(ex)))
                add_plan_detail = u"计划创建失败,失败原因为:{}".format(str(ex))

            response.setdefault("result", add_plan_flag)
            response.setdefault("detail", add_plan_detail)
            response.setdefault("rule_id", rule_id)
            return HTTPResponse(status=200, body=response)

        # 查询计划信息(参数给了rule_id,查询单条计划,否在查询所有计划)
        @self.rule_app.route('/rules/query', method='POST')
        def query_plan():
            response = dict()
            result = 1
            data = list()
            try:
                # 判断查询条件中是否有rule_id
                try:
                    rule_id = request.json['rule_id']
                except:
                    rule_id = None
                if rule_id:
                    query_sql = "select rule_id, rule_name, Cron, spider_status, NextFireTime from {} where is_delete=0 and rule_id={};".format(SPIDER_PLAN, rule_id)
                else:
                    query_sql = "select rule_id, rule_name, Cron, spider_status, NextFireTime from {} where is_delete=0;".format(SPIDER_PLAN)
                rows = self.sqlite_helper.sqlite_query(query_sql).fetchall()
                if rows:
                    for row in rows:
                        temp_dict = dict()
                        temp_dict.setdefault("rule_id", row[0])
                        temp_dict.setdefault("rule_name", row[1])
                        temp_dict.setdefault("Type", row[2])
                        temp_dict.setdefault("Status", row[3])
                        temp_dict.setdefault("NextFireTime", row[4])
                        data.append(temp_dict)
                    detail = u"计划查询成功"
                    result = 0
                else:
                    if not rule_id:
                        detail = u"当前还未添加过计划或已有计划已经全部被停止"
                    else:
                        detail = u"按rule_id={}查询的条件未查找出计划".format(rule_id)
            except Exception as ex:
                logging.error(u"查询计划时发生异常,异常原因为:{}".format(str(ex)))
                detail = u"查询计划时发生异常,异常原因为:{}".format(str(ex))
            response.setdefault("result", result)
            response.setdefault("detail", detail)
            response.setdefault("data", data)
            return HTTPResponse(status=200, body=response)

    # def do_POST(self):
    #     path, args = urllib.splitquery(self.path)
    #     data = self.rfile.read(int(self.headers['content-length']))
    #     self.do_action(path, data)

    # 消息处理函数
    # def do_action(self, path, msg):
    #     logging.info('接收消息地址:{}，消息内容:{}'.format(path, msg))
    #     msg = json_loads(msg)
    #     response = None
    #     if path == "/rules/add":
    #         response = self.add_plan(msg)
    #     elif path == "/rules/update":
    #         response = self.update_plan(msg)
    #     elif path == "/rules/query":
    #         response = self.query_plan(msg)
    #     elif path == "/rules/delete":
    #         response = self.delete_plan(msg)
    #     elif path == "/rules/start":
    #         response = self.start_plan(msg)
    #     elif path == "/rules/stop":
    #         response = self.stop_plan(msg)
    #     detail = response.get("detail", None)
    #     if detail:
    #         logging.info(u"此次post的执行执行结果为:{},请求路径为:{}".format(detail, path))
    #     self.output(response)

    # 将json字符串转换为json

        # 删除计划
        @self.rule_app.route('/rules/delete', method='POST')
        def delete_plan():
            response = dict()
            result = 1
            rule_id = None
            try:
                rule_id = request.json['rule_id']
                update_sql = "update {} set is_delete=1 where rule_id={};".format(SPIDER_PLAN, rule_id)
                self.sqlite_helper.sqlite_update_delete_insert(update_sql)
                flag, detail = self.execute_spider.stop_spider(rule_id=rule_id, param=0)
                if flag:
                    detail = u"成功删除计划"
                    result = 0
            except Exception as ex:
                error_message = u"删除计划发生异常,异常原因为:{}".format(str(ex))
                logging.error(error_message)
                detail = error_message

            response.setdefault("result", result)
            response.setdefault("detail", detail)
            response.setdefault("rule_id", rule_id)
            return HTTPResponse(status=200, body=response)

        # 修改计划(给什么参数修改什么参数)
        @self.rule_app.route('/rules/update', method='POST')
        def update_plan():
            response = dict()
            result = 1
            rule_id = request.POST["rule_id"]
            rule_name = None
            try:
                # 修改计划名称和url
                try:
                    rule_json = request.POST["rule_json"]
                    if rule_json:
                        rule_json = json.loads(rule_json)
                        rule_name = rule_json.get("rule_name", None)
                        collect_url_json = rule_json.get("urls", None)
                        if collect_url_json:
                            collect_url_json_string = json.dumps(collect_url_json)
                        else:
                            collect_url_json_string = None
                        if rule_name:
                            rule_path = self.get_rule_file_path(rule_id)
                            # 先查询当前计划的规则文件的文件名
                            query_sql = "select rule_name from {} where rule_id={};".format(SPIDER_PLAN, rule_id)
                            query_res = self.sqlite_helper.sqlite_query(query_sql).fetchone()
                            if query_res:
                                original_rule_name = query_res[0]
                                original_rule_path = os.path.join(rule_path, original_rule_name + ".xml")
                            update_sql = "update {} set rule_name='{}' where rule_id={};".format(SPIDER_PLAN, rule_name, rule_id)
                            self.sqlite_helper.sqlite_update_delete_insert(update_sql)
                            current_rule_path = os.path.join(rule_path, rule_name + ".xml")
                            # 更改本地规则文件的名字
                            os.rename(original_rule_path, current_rule_path)
                        if collect_url_json_string:
                            update_sql = "update {} set urls='{}' where rule_id={};".format(SPIDER_PLAN, collect_url_json_string, rule_id)
                            self.sqlite_helper.sqlite_update_delete_insert(update_sql)
                except:
                    pass
                # 修改cron表达式
                try:
                    rule_cron = request.POST["rule_cron"]
                    if rule_cron:
                        try:
                            next_time = cron_to_date(rule_cron)
                        except Exception as ex:
                            logging.error(u"Cron表达式转化失败,此次计划不进行修改, 错误原因为:{}".format(str(ex)))
                            response.setdefault("result", result)
                            detail = u"计划修改失败,原因:Cron表达式转化失败"
                            response.setdefault("detail", detail)
                            response.setdefault("rule_id", rule_id)
                            return HTTPResponse(status=200, body=response)
                    update_sql = "update {} set Cron='{}', NextFireTime='{}' where rule_id={};".format(SPIDER_PLAN, rule_cron, next_time, rule_id)
                    self.sqlite_helper.sqlite_update_delete_insert(update_sql)
                except:
                    pass
                # 修改规则文件
                try:
                    rule_file = request.POST["rule_file"]
                    if rule_file:
                        if not rule_name:
                            query_sql = "select rule_name from {} where rule_id={};".format(SPIDER_PLAN, rule_id)
                            query_res = self.sqlite_helper.sqlite_query(query_sql).fetchone()
                            if query_res:
                                rule_name = query_res[0]
                        rule_path = self.get_rule_file_path(rule_id)
                        if not os.path.isdir(rule_path):
                            os.makedirs(rule_path)
                        rule_path = os.path.join(rule_path, rule_name + ".xml")
                        rule_file.save(rule_path, overwrite=True)
                except:
                    pass
                result = 0
                detail = u"计划修改成功"
            except Exception as ex:
                error_message = u"修改计划发生异常,异常原因为:{}".format(str(ex))
                logging.error(error_message)
                detail = error_message

            response.setdefault("result", result)
            response.setdefault("detail", detail)
            response.setdefault("rule_id", rule_id)
            return HTTPResponse(status=200, body=response)

        # 启动计划
        @self.rule_app.route('/rules/start', method='POST')
        def start_plan():
            response = dict()
            result = 1
            rule_id = None
            try:
                rule_id = request.json['rule_id']
                spider_kwargs = self.execute_spider.check_plan(rule_id)
                if spider_kwargs:
                    # 调用爬虫启动函数
                    if not self.execute_spider.start_spider_now(kwargs=spider_kwargs):
                        detail = u"计划执行中或等待中,不可再次启动计划"
                    else:
                        detail = u"成功启动计划"
                        result = 0
                else:
                    detail = u"未查询到rule_id={}的计划或计划已被删除,请重新尝试".format(rule_id)
                    result = 1
            except Exception as ex:
                error_message = u"开始计划时发生异常,异常原因为:{}".format(str(ex))
                logging.error(error_message)
                detail = error_message
            response.setdefault("result", result)
            response.setdefault("detail", detail)
            response.setdefault("rule_id", rule_id)
            return HTTPResponse(status=200, body=response)

        # 停止计划
        @self.rule_app.route('/rules/stop', method='POST')
        def stop_plan():
            response = dict()
            result = 1
            rule_id = None
            try:
                rule_id = request.json['rule_id']
                if rule_id:
                    # # 将数据库中状态标志为置为1
                    # update_sql = "update {} set is_stop=1, spider_status='{}' where rule_id={};".format(SPIDER_PLAN, u"已停止", rule_id)
                    # self.sqlite_helper.sqlite_update_delete_insert(update_sql)

                    flag, detail = self.execute_spider.stop_spider(rule_id=rule_id, param=1)
                    if flag:
                        result = 0
                else:
                    detail = u"rule_id为空,无法停止计划"
            except Exception as ex:
                error_message = u"停止计划发生异常,异常原因为:{}".format(str(ex))
                logging.error(error_message)
                detail = error_message
            response.setdefault("result", result)
            response.setdefault("detail", detail)
            response.setdefault("rule_id", rule_id)
            return HTTPResponse(status=200, body=response)

        @self.rule_app.route('/rules/test', method='POST')
        def test():
            data = {"aaa": 13}
            print request.POST["rule_id"]
            return HTTPResponse(status=200, body=data)

    def json_dumps(self, msg):
        try:
            if msg:
                msg = json.dumps(msg)
            return msg
        except Exception as ex:
            logging.error(u"将json字符串转换为json发生异常,异常原因为:{}".format(str(ex)))
        return None

    # 将收到的规则文件本地化
    @staticmethod
    def write_rule_file(rule_name, rule_path, rule_file):
        try:
            # 先判断文件夹是否存在,不存在,先创建
            if not os.path.isdir(rule_path):
                os.makedirs(rule_path)
            # 拼接规则文件的路径
            rule_path = os.path.join(rule_path, rule_name + ".xml")
            # 如果文件已存在,先删除,再储存
            if os.path.isfile(rule_path):
                os.remove(rule_path)
            with open(rule_path, "wb") as write:
                write.write(rule_file)
            return True
        except Exception as ex:
            logging.error(u"规则文件本地化时发生异常,异常原因为:{}".format(str(ex)))
        return False

    @staticmethod
    def get_rule_file_path(rule_id):
        if isinstance(rule_id, int):
            rule_id = str(rule_id)
        path = os.path.join(local_rule_file_path, rule_id)
        return path

    # 获取当前时间的字符串形式
    @staticmethod
    def get_time_string():
        struct_time = time.localtime(int(time.time()))
        return time.strftime("%Y-%m-%d %H:%M:%S", struct_time)


def poll_plan():
    global SPIDER_PROCESS
    execute_spider = ExecuteSpiderByProcess()
    # 轮询数据库的计划信息
    while True:
        query_sql = "select * from {} where is_delete=0 and is_stop=0;".format(SPIDER_PLAN)
        query_res = execute_spider.sqlite_helper.sqlite_query(query_sql).fetchall()
        if query_res:
            struct_time = time.localtime(int(time.time()))
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", struct_time)
            for row in query_res:
                try:
                    next_fire_time = row[3]
                    rule_id = row[1]
                    # 达到执行时间
                    if now_time >= str(next_fire_time):
                        # 计划未在执行
                        if not SPIDER_PROCESS.get(str(rule_id)):
                            spider_kwargs = execute_spider.format_spider_kwargs(row)
                            # 调用爬虫启动函数
                            execute_spider.execute_spider(kwargs=spider_kwargs)
                except Exception as ex:
                    logging.error(u"启动此计划发生异常,异常原因为:{}".format(str(ex)))
                    logging.error(u"计划信息为:{}".format(row))
        # 10s轮询一次数据库的计划
        time.sleep(10)


if __name__ == '__main__':
    logging.info(u"初始化sqlite")
    sqlite_helper = SqliteHelper()
    sqlite_helper.sqlite_create_table()
    thread = threading.Thread(target=poll_plan)
    thread.start()
    logging.info(u"启动http服务监听,监听的HOST:{},PORT:{}".format(http_host, http_port))
    # http_server = HTTPServer((http_host, http_port), RequestHandlers)
    # http_server.serve_forever()
    http_server = RequestHandlers(local_ip=http_host, local_port=http_port, )
    try:
        run(http_server.rule_app, host=http_host, port=http_port, debug=True)
    except Exception as err:
        logging.error(u"start http server error, the exception is:{}".format(str(err)))
    thread.join()
