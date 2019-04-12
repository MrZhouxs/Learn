# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/4/4/0004 14:21:04
# Author  : little star
# Func: url拼接
import scrapy

from CrawlDemos.utils.url_parse import url_join, get_img_name_by_url


class SecondCrawl(scrapy.Spider):
    """
    如果多个爬虫下，每个爬虫需要自己的个性设置settings，可以在每个爬虫里设置custom_settings
    """
    name = "second_crawl"

    def __init__(self, *param):
        super(SecondCrawl, self).__init__(name=self.name)

    def start_requests(self):
        url = "https://auth.alipay.com/login/index.htm"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        images = response.xpath('//*[@id="lg"]/img/@src').extract()
        temp = url_join(response.url, images)
        for each in temp:
            _ = get_img_name_by_url(each)
