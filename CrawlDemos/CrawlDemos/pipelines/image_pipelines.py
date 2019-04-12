# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/4/1/0001 16:09:12
# Author  : little star
# 演示图片下载
from scrapy import Request
# 当在pipelines中DropItem时，后续的pipelines不会再处理该item
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from CrawlDemos.items.items import ImageItems
from CrawlDemos.utils.url_parse import get_img_name_by_url


class CustomImagePipelines(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        """
        返回保存图片的文件名
        :param request: 当前下载对应的Request对象
        :param response:
        :param info:
        :return:
        """
        url = request.url
        file_name = get_img_name_by_url(url)
        return file_name

    def item_completed(self, results, item, info):
        """
        它是当单个Item完成下载时的处理方法
        :param results: 该Item对应的下载结果，包含了下载成功或失败的信息
        example: [(True,{'url':'https://user-gold-cdn.xitu.io/2018/5/9/16342f8eefeced62?imageslim',
            'path': 'rest.jpg', 'checksum': '528a40a601adc48645ac4e52fb4a19f8'})]
        :param item:
        :param info:
        :return:
        """
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('Image Downloaded Failed')
        return item

    def get_media_requests(self, item, info):
        if isinstance(item, ImageItems):
            yield Request(item['url'])

