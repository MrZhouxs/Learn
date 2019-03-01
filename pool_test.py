# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/2/27/0027 17:49:20
# Author  : little star
# Func: 线程池和进程池
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import time

process_poll = ProcessPoolExecutor()


def add(x, y):
    time.sleep(2)
    return x + y


def process_test():
    now = time.time()
    processes = list()
    for i in range(0, 3):
        # 异步执行
        obj = process_poll.submit(add, i, i + 1)
        processes.append(obj)
    for each in processes:
        # 调用result时会阻塞
        print(each.result())
    print(time.time() - now)


def thread_test():
    # 线程池的个数，默认是CPU个数的两倍
    # 任务数量大于线程池数量时，会进行等待
    t = ThreadPoolExecutor(2)
    threads = list()
    now = time.time()
    for i in range(0, 3):
        obj = t.submit(add, i, i + 1)
        threads.append(obj)
    for each in threads:
        # 调用result时会阻塞
        print(each.running())
    print(time.time() - now)
    print(len(threads))


if __name__ == '__main__':
    process_test()
    # thread_test()
