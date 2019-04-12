# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/4/8/0008 16:29:41
# Author  : little star
# Func: LinkExtractor如何使用

import scrapy
from scrapy.linkextractors import LinkExtractor


class LinkSpider(scrapy.Spider):
    name = "link_spider"

    def start_requests(self):
        url = "http://baike.baidu.com/fenlei/%E6%94%BF%E6%B2%BB%E4%BA%BA%E7%89%A9"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # 使用LinkExtractor提取链接
        link = LinkExtractor(restrict_xpaths=('//*[@id="pageIndex"]', ))
        links = link.extract_links(response)
        if links:
            for each in links:
                _ = each.url

        link_2 = LinkExtractor(restrict_xpaths=('//*[@class="grid-list grid-list-spot"]', ),
                               allow=('/(.*?).htm', ))
        link_2_links = link_2.extract_links(response)
        if link_2_links:
            for each in link_2_links:
                _ = each.url

        """
        LinkExtractor会在提取链接时默认忽略以下扩展名，如果要提取以下链接得话，
        需要给出deny_extensions参数，给出得参数是不被提取得（给出需要得扩展名得其它参数）
        IGNORED_EXTENSIONS = [
            # images
            'mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif',
            'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps', 'svg',
            # audio
            'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff',
            # video
            '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv',
            'm4a', 'm4v', 'flv',
            # office suites
            'xls', 'xlsx', 'ppt', 'pptx', 'pps', 'doc', 'docx', 'odt', 'ods', 'odg',
            'odp',
            # other
            'css', 'pdf', 'exe', 'bin', 'rss', 'zip', 'rar',
        ]
        """
        # 提取图片链接
        image_link = LinkExtractor(restrict_xpaths=('//*[@class="grid-list grid-list-spot"]', ),
                                   tags=("img", ), attrs=("src", ), deny_extensions=("!!!", ))
        image_link_links = image_link.extract_links(response)
        print(len(image_link_links))
        print(image_link_links)
