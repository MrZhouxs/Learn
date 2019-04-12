# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/3/28/0028 17:48:59
# Author  : little star
# Func: 自定义proxy中间件
import random


class CustomProxyMiddleware(object):
    proxyList = [
        '106.12.214.231:80'
    ]

    def process_request(self, request, spider):
        # Set the location of the proxy
        pro_adr = random.choice(self.proxyList)
        print("USE PROXY -> " + pro_adr)
        # 在request上添加proxy，该方法不要返回值
        request.meta['proxy'] = "http://" + pro_adr
