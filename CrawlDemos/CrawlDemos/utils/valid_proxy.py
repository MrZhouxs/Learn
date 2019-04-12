# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/3/29/0029 10:08:43
# Author  : little star
import requests


class IsValidProxy(object):

    @classmethod
    def is_valid(cls, proxy):
        """
        验证代理IP是否有用
        :param proxy: 代理IP，格式 http://host:port
        :return:
        """
        try:
            requests.get("http://www.baidu.com/", proxies={"http": proxy})
            return True
        except:
            return False
