# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/3/28/0028 10:11:41
# Author  : little star
import scrapy
from scrapy import Selector
from CrawlDemos.items.items import CrawldemosItem, ImageItems
from CrawlDemos.items.custom_items import MainItemLoader, MetaItemLoader


class CrawlSpider(scrapy.Spider):
    name = "crawl_spider"
    # 测试cookies的url
    start_urls = ["http://exercise.kingname.info/exercise_login_success"]

    def __init__(self):
        super(CrawlSpider, self).__init__(name=self.name)

    def parse(self, response):
        item = CrawldemosItem()
        item2 = ImageItems()
        print(response.url)
        # print(response.text)
        item["name"] = "test1"
        item["age"] = "123"
        item2["url"] = "https://user-gold-cdn.xitu.io/2018/5/9/16342f8eefeced62?imageslim"
        yield item
        yield item2
        # 嵌套的item如何赋值
        main_loader = MainItemLoader(selector=Selector(response))
        main_loader.add_value("title", "test")
        main_loader.add_value("price", 12.3)
        main_loader.add_value("meta", self.add_meta(response))
        yield main_loader.load_item()

    def add_meta(self, response):
        meta_loader = MetaItemLoader(selector=Selector(response))
        meta_loader.add_value("url", response.url)
        meta_loader.add_value("added_on", "now")
        return meta_loader.load_item()
