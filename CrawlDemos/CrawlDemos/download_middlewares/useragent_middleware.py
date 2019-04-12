# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/3/28/0028 17:43:46
# Author  : little star
# Func: 自定义User-Agent中间件(fake_useragent获取随机的User-Agent需要联网)

from fake_useragent import FakeUserAgent
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class CustomUserAgentMiddleware(UserAgentMiddleware):
    """
    通过fake_useragent库随机生成User-Agent，自定义爬虫的User-Agent
    """
    ua = FakeUserAgent()

    def process_request(self, request, spider):
        if self.ua:
            request.headers['User-Agent'] = self.ua.random
