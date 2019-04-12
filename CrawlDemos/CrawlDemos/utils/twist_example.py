# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/4/3/0003 15:03:46
# Author  : little star
# Func: 了解Twisted编程
from twisted.web.client import getPage
from twisted.internet import reactor


class TwistedExample(object):
    def __init__(self):
        pass

    def lower_callback(self, content):
        print("------------ lower_callback --------------")
        # print(content)
        return content

    def high_callback(self, content, param):
        print("------------ high_callback --------------")
        print(param)
        a = "1" + 1

    def error_callback(self, error):
        # 出现错误时被调用
        print("------------ error -----------------------")
        print(error)


if __name__ == '__main__':
    url = "http://www.baidu.com/"
    err_url = "http://twistedmatrix.com/does-not-exist"
    deferred = getPage(url=url.encode("utf8"))
    a = TwistedExample()
    deferred.addCallback(a.lower_callback)
    # lower_callback返回的数据回自动传递给high_callback中
    deferred.addCallback(a.high_callback, 1)
    deferred.addErrback(a.error_callback)
    # 4s关闭异步程序
    reactor.callLater(4, reactor.stop)
    reactor.run()
