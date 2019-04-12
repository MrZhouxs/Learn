# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawldemosItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    age = scrapy.Field(serializer=int)


class ImageItems(scrapy.Item):
    url = scrapy.Field()
