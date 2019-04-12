# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/4/3/0003 17:32:03
# Author  : little star
# Func: 嵌套的item
from scrapy import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


class MetaItem(Item):
    url = Field()
    added_on = Field()


class MainItem(Item):
    price = Field()
    title = Field()
    meta = Field(serializer=MetaItem)


class MainItemLoader(ItemLoader):
    default_item_class = MainItem
    default_output_processor = TakeFirst()


class MetaItemLoader(ItemLoader):
    default_item_class = MetaItem
    default_output_processor = TakeFirst()
