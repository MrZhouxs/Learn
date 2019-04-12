# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/4/3/0003 9:58:38
# Author  : little star
# Func: 重写RetryMiddleware中间件

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message


class CustomRetryMiddleWare(RetryMiddleware):
    """默认的RetryMiddleware涉及到settings.py文件中的几个量：
        RETRY_ENABLED: 用于开启中间件，默认为TRUE
        RETRY_TIMES: 重试次数, 默认为2
        RETRY_HTTP_CODES: 遇到哪些返回状态码需要重试, 一个列表，默认为[500, 503, 504, 400, 408]
        RETRY_PRIORITY_ADJUST：调整相对于原始请求的重试请求优先级，默认为-1
    """
    def process_response(self, request, response, spider):
        # 如果爬虫中定义了不需要重试，则不做处理
        if request.meta.get('dont_retry', False):
            return response
        # 重写重试的逻辑伪代码
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            # _retry方法有如下作用：
            # 1、对request.meta中的retry_time进行+1
            # 2、将retry_times和max_retry_time进行比较，如果前者小于等于后者，
            # 利用copy方法在原来的request上复制一个新request，并更新其retry_times，
            # 并将dont_filter设为True来防止因url重复而被过滤
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            # 重写重试的逻辑伪代码
            ...
            return self._retry(request, exception, spider)
