# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/3/28/0028 11:23:29
# Author  : little star


class CustomDownloaderMiddleware(object):

    def process_request(self, request, spider):
        """
        当每个request通过下载中间件时，该方法被调用。
        process_request()必须返回其中之一: 返回None、返回一个Response对象、返回一个Request对象
        或raise IgnoreRequest。
        如果其返回None，Scrapy将继续处理该request，执行其他的中间件的相应方法，
        直到合适的下载器处理函数(download handler)被调用， 该request被执行(其response被下载)。
        如果其返回Response对象，Scrapy将不会调用任何其他的process_request()或process_exception()
        方法，或相应地下载函数；其将返回该response。已安装的中间件的process_response()方法
        则会在每个response返回时被调用。
        如果其返回Request对象，Scrapy则停止调用 process_request方法并重新调度返回的request。
        当新返回的request被执行后， 相应地中间件链将会根据下载的response被调用。
        如果其raise一个 IgnoreRequest 异常，则安装的下载中间件的process_exception()
        方法会被调用。如果没有任何一个方法处理该异常，则request的errback(Request.errback)方法会被
        调用。如果没有代码处理抛出的异常， 则该异常被忽略且不记录(不同于其他异常那样)。
        :param request: Request 对象 – 处理的request
        :param spider: Spider 对象 – 该request对应的spider
        :return:
        """
        # download_url = request.url
        # headers = request.headers
        # response = self.session.get(url=download_url)
        # return HtmlResponse(url=download_url, body=response.text, request=request,
        #                     encoding="utf-8", status=response.status_code, headers=headers)
        # TODO twisted异步下载
        pass

    def process_response(self, request, response, spider):
        """
        process_request()必须返回以下之一: 返回一个Response对象、返回一个Request对象或raise一个IgnoreRequest异常。
        如果其返回一个 Response (可以与传入的response相同，也可以是全新的对象)，
        该response会被在链中的其他中间件的 process_response() 方法处理。
        如果其返回一个 Request 对象，则中间件链停止，返回的request会被重新调度下载。
        处理类似于 process_request() 返回request所做的那样。
        如果其抛出一个 IgnoreRequest 异常，则调用request的errback(Request.errback)。
        如果没有代码处理抛出的异常，则该异常被忽略且不记录(不同于其他异常那样)
        :param request: Request 对象 – response所对应的request
        :param response: Response 对象 – 被处理的response
        :param spider: Spider 对象 – response所对应的spider
        :return:
        """
        return response

    def process_exception(self, request, exception, spider):
        """
        当下载处理器(download handler)或 process_request() (下载中间件)
        抛出异常(包括 IgnoreRequest 异常)时， Scrapy调用 process_exception()
        process_exception()应该返回以下之一: 返回None、一个Response对象、或者一个Request对象。
        如果其返回None，Scrapy将会继续处理该异常，接着调用已安装的其他中间件的process_exception()
        方法，直到所有中间件都被调用完毕，则调用默认的异常处理。
        如果其返回一个Response对象，则已安装的中间件链的process_response()方法被调用。
        Scrapy将不会调用任何其他中间件的process_exception()方法。
        如果其返回一个Request对象，则返回的request将会被重新调用下载。
        这将停止中间件的process_exception()方法执行，就如返回一个response的那样
        :param request: 是 Request 对象 – 产生异常的request
        :param exception: Exception 对象 – 抛出的异常
        :param spider: Spider 对象 – request对应的spider
        :return:
        """
        pass


