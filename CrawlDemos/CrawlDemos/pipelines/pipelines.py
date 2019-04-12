# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from CrawlDemos.items.items import CrawldemosItem


class CrawlDemosPipeline(object):
    """
    可自定义实现Item Pipeline
    可重写的方法：
    open_spider(self, spider)
    close_spider(self, spider)
    from_crawler(cls, crawler)
    process_item(self, item, spider)（必须要实现）
    """

    def process_item(self, item, spider):
        """
        如果它返回的是Item对象，那么此Item会被低优先级的Item Pipeline的process_item()方法处理，直到所有的方法被调用完毕。
        如果它抛出的是DropItem异常，那么此Item会被丢弃，不再进行处理
        :param item: Item对象
        :param spider:
        :return:
        """
        if isinstance(item, CrawldemosItem):
            print("CrawlDemosItem")
        return item
