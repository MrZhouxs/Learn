# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/3/28/0028 17:23:49
# Author  : little star
# Func: 利用selenium的webdriver.Chrome来加载动态页面
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from fake_useragent import FakeUserAgent

# Chrome 驱动
CHROME_EXECUTE_PATH = ""


class ChromeDownloaderMiddleware(object):
    def __init__(self):
        service_args = list()
        options = webdriver.ChromeOptions()
        options.add_argument("user-agent='{}'".format(FakeUserAgent().random))
        options.add_argument('--headless')  # 设置无界面
        options.add_argument("--disable-images")    # 禁用图像
        # options.add_argument("–start-maximized")    # 启动Google Chrome就最大化
        # options.add_argument("--disable-plugins")   # 禁止加载所有插件
        # options.add_argument("--disable-javascript")    # 禁用JavaScript
        # options.add_argument("--lang=zh-CN")    # 设置语言为简体中文
        if CHROME_EXECUTE_PATH:
            self.driver = webdriver.Chrome(executable_path=CHROME_EXECUTE_PATH,
                                           service_args=service_args, chrome_options=options)
        else:
            self.driver = webdriver.Chrome(service_args=service_args, chrome_options=options)

    def __del__(self):
        try:
            if self.driver:
                self.driver.close()
        except Exception as ex:
            print(ex)

    def process_request(self, request, spider):
        try:
            print('Chrome driver begin...')
            # 在无窗口的情况下只能如下设置窗口大小
            # self.driver.set_window_size(1920, 1080)

            self.driver.get(request.url)  # 获取网页链接内容
            self.driver.save_screenshot("test.png")
            return HtmlResponse(url=request.url, body=self.driver.page_source, request=request,
                                encoding='utf-8', status=200)  # 返回HTML数据
        except TimeoutException:
            return HtmlResponse(url=request.url, request=request, encoding='utf-8', status=500)
        finally:
            print('Chrome driver end...')
