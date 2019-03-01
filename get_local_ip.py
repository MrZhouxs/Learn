# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/3/1/0001 13:31:11
# Author  : little star
import os
import psutil


def get_ip():
    """
    获取局域网ip
    :return:
    """
    netcard_info = []
    info = psutil.net_if_addrs()
    for k, v in info.items():
        for item in v:
            ip = item[1]
            if item[0] == 2 and not ip == '127.0.0.1':
                # 对一个ip进行ping两次，等待1s，返回结果，1为失败，0为成功
                a = os.system('ping -n 2 -w 1 %s' % ip)
                if a == 0:
                    netcard_info.append((k, ip))
    return netcard_info
