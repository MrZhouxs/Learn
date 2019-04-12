# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/3/28/0028 10:09:33
# Author  : little star
import os
from scrapy import cmdline
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess

from CrawlDemos.spiders.crawl import CrawlSpider
from CrawlDemos.spiders.second_crawl import SecondCrawl


# scrapy运行时，需要将scrapy.cfg所在的路径加到当前工作环境
# 这样才可以不论在什么路径下都能运行爬虫
current_path = os.path.dirname(__file__)
os.chdir(current_path)


def run():
    # 运行一次cmdline.execute后不会继续往下运行，整个项目就会停止
    cmdline.execute("scrapy crawl second_crawl".split(" "))
    # cmdline.execute("scrapy crawl link_spider".split(" "))


def run_multi_crawl():
    """
    同一个scrapy项目里运行多个爬虫，不能给爬虫参数信息
    :return:
    """
    setting = get_project_settings()
    process = CrawlerProcess(setting)
    for spider_name in process.spider_loader.list():
        process.crawl(spider_name)
    process.start()
    print("----------------------- end -------------------------")


def run_crawl_by_function():
    """
    以起函数的方式启动爬虫
    :return:
    """
    # 先初始化一次SecondCrawl的__init__方法
    crawl = SecondCrawl("haha")
    # CrawlerProcess不给setting，项目的settings设置用不了
    setting = get_project_settings()
    process = CrawlerProcess(setting)
    # process.crawl会再次初始化一次SecondCrawl的__init__方法，可以再给一次参数
    process.crawl(crawl)
    process.start()


if __name__ == '__main__':
    run()
    # run_multi_crawl()
    # run_crawl_by_function()
