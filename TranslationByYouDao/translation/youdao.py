# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/3/27/0027 10:30:23
# Author  : little star
import hashlib
import json
import random
import time
from urllib import parse, request


HEADERS = {
    "Host": "fanyi.youdao.com",
    "Connection": "keep-alive",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Origin": "http://fanyi.youdao.com",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Referer": "http://fanyi.youdao.com/",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cookie": "fanyi-ad-id=46607; fanyi-ad-closed=1; OUTFOX_SEARCH_USER_ID=518495945@10.168.8.61; OUTFOX_SEARCH_USER_ID_NCOO=864597530.4941442; JSESSIONID=aaa8f-DvDX97p-CzgE7qw; ___rl__test__cookies=1530014068222",
}


class Translation(object):
    def __init__(self):
        self.base_url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'

    def get_sign(self, content, salt):
        md5 = hashlib.md5()
        content = 'fanyideskweb' + content + str(salt) + 'ebSeFb%=XZ%T[KZ)c(sy!'
        md5.update(content.encode("utf8"))
        sign = md5.hexdigest()
        return sign

    def translate(self, content):

        salt = int(time.time() * 1000) + int(random.random() * 10)
        sign = self.get_sign(content, salt)
        form = {
            "i": content,
            "from": "AUTO",
            "to": "AUTO",
            "smartresult": "dict",
            "client": "fanyideskweb",
            "salt": salt,
            "sign": sign,
            "doctype": "json",
            "version": "2.1",
            "keyfrom": "fanyi.web",
            "action": "FY_BY_REALTIME",
            "typoResult": "false",
        }

        form = parse.urlencode(form)
        HEADERS["Content-Length"] = len(form)
        req = request.Request(self.base_url, headers=HEADERS, data=bytes(form, encoding='utf-8'))
        response = request.urlopen(req)
        data = response.read().decode('utf-8')
        data = json.loads(data)
        if "translateResult" in data:
            for each in data["translateResult"][0]:
                temp = each.get("tgt")
                return temp
        return None
