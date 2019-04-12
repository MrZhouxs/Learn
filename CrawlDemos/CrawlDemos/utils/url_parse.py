# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/4/8/0008 13:39:27
# Author  : little star
# Func: url处理
import urllib.parse


def url_join(base, src):
    """
    url拼接
    :param base: 基础url
    :param src: 待拼接的url
    :return:
    """
    if isinstance(src, (list, tuple, set)):
        for url in src:
            try:
                temp = urllib.parse.urljoin(base, url)
                yield temp
            except ValueError:
                pass
    else:
        try:
            dst = urllib.parse.urljoin(base, src)
            return dst
        except:
            pass
    if base:
        return base
    if src:
        return src


def get_img_name_by_url(url):
    """
    根据url的连接获取图片的图片名
    example:
        https://www.baidu.com/img/bd_logo1.png           -> bd_logo1.png
        https://www.baidu.com/img/bd_logo1.png?qua=high  -> bd_logo1.png
    :param url: 图片url
    :return:
    """
    temp = urllib.parse.urlsplit(url)
    url_path = temp.path
    if url_path:
        split_path = url_path.split("/")
        return split_path[-1]
    else:
        return url
