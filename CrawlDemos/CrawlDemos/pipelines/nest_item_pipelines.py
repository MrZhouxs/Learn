# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/4/3/0003 17:41:23
# Author  : little star
# Func: 嵌套的item经过pipelines的处理
from CrawlDemos.items.custom_items import MainItem


class NestItemPipelines(object):
    def process_item(self, item, spider):
        # 判断item是什么类型，和爬虫那赋值的对象是不一样的
        # <class 'CrawlDemos.items.custom_items.MainItem'>
        if isinstance(item, MainItem):
            print(item)
        return item
