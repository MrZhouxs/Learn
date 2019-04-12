# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/4/3/0003 11:17:12
# Author  : little star
# Func: 异步插入数据

import pymysql
from twisted.enterprise import adbapi
from CrawlDemos.items.items import CrawldemosItem


class AsyncDbPipelines(object):
    def __init__(self, host, port, user, password, db_name, charset="utf8"):
        param = dict(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db_name,
            charset=charset,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.db_pool = adbapi.ConnectionPool("pymysql", **param)

    @classmethod
    def from_crawler(cls, crawler):
        # 获取settings中的信息
        # 必须要返回cls的对象，否则process_item不会被处理
        settings = crawler.settings
        host = settings.get("host", "127.0.0.1")
        port = settings.get("port", 3306)
        user = settings.get("user", "root")
        password = settings.get("password", "root")
        charset = settings.get("charset", "utf8")
        db_name = settings.get("db_name", "spider")
        return cls(host, port, user, password, db_name, charset)

    def process_item(self, item, spider):
        """
        如果它返回的是Item对象，那么此Item会被低优先级的Item Pipeline的process_item()方法处理，直到所有的方法被调用完毕。
        如果它抛出的是DropItem异常，那么此Item会被丢弃，不再进行处理
        :param item: Item对象
        :param spider:
        :return:
        """
        # 判断iten是属于哪一个Item
        if isinstance(item, CrawldemosItem):
            # 使用数据库连接池对象进行数据库操作,自动传递cursor对象到第一个参数
            handler = self.db_pool.runInteraction(self.db_option, item)
            handler.addErrback(self.on_error, spider)
        return item

    def db_option(self, cursor, item):
        """
        插入数据的具体操作，如果有错误的话，不会报错，但也不执行错误的回调函数
        :param cursor: 操作数据库的对象
        :param item: Item对象
        :return:
        """
        print("---------------------------------------")
        sql = "insert into test (name, age) VALUES ('andy', 25)"
        # execute()之后,不需要再进行commit()，连接池内部会进行提交的操作
        cursor.execute(sql)

    def on_error(self, error, spider):
        print("--------------- error -----------------------")
        print(error)
