# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/4/2/0002 10:53:27
# Author  : little star
# Func: cookie中间件
import requests


class CustomCookieMiddleWare(object):
    def get_cookie(self):
        url = "http://exercise.kingname.info/exercise_login"
        data = {"username": "kingname", "password": "genius", "rememberme": "Yes"}
        # 注意重定向问题
        response = requests.post(url=url, data=data, allow_redirects=False)
        cookie = response.cookies.get_dict()
        return cookie

    def process_request(self, request, spider):
        # 设置cookies(type: dict)
        request.cookies = self.get_cookie()
        return None

    def process_response(self, request, response, spider):
        if response.status in [302, 301]:
            # 获取重定向的地址
            # redirect_url = response.next.url
            request.cookies = self.get_cookie()
            return request
        return response
