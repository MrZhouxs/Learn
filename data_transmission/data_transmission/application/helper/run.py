#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time

from data_transmission.application.helper import LOG_WARNING


def wrapper(func, *args, **kwargs):
    """
    处理函数执行过程中出现的异常,直到函数执行成功，并返回执行函数的返回值.
    执行间隔: 5s.
    :param func: 函数对象.
    :return: 函数对象返回值.
    """
    while True:
        try:
            result = func(*args, **kwargs)
            break
        except Exception as ex:
            LOG_WARNING.error(u"执行插入操作时，发生异常，异常原因：{}".format(str(ex)))
            time.sleep(10)
    return result
