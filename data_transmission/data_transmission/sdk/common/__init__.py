""" sdk common package

Singleton meta class, for single class instance

NewThread is implement thread option class
start_thread is a quickly start thread function
"""
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import multiprocessing
import time
import subprocess
from oslo_log import log
LOG = log.getLogger('log')


class Singleton(type):
    """
    meta class
    """

    def __init__(self, *args, **kwargs):
        self.__instance = None
        super(Singleton, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super(Singleton, self).__call__(*args, **kwargs)
        return self.__instance


class NewThread(threading.Thread):
    """
    thread implement class
    """

    def __init__(self, name, proc):
        """
        init func
        :param str name: thread name
        :param callback proc: callback function
        """
        threading.Thread.__init__(self)
        self.name = name
        self.proc = proc

    def stop(self):
        """
        stop thread
        """
        self._stop()

    def run(self):
        """
        thread run function
        """
        self.proc()


def start_thread(name, proc):
    """
    quick start thread function
    :param str name: thread name
    :param callback proc: thread run function
    :return:
    """
    new_thread = NewThread(name, proc)
    new_thread.start()
    return new_thread


def start_process(name, proc):
    """
    quick start process function
    :param str name: process name
    :param callback proc: process run function
    :return:
    """
    new_process = multiprocessing.Process(name=name, target=proc)
    new_process.start()
    time.sleep(3)
    return new_process


def stop_process(pid):
    try:
        temp = 'kill -9 {}'.format(pid)
        subprocess.Popen(temp, shell=True, stdout=subprocess.PIPE)
    except Exception as e:
       LOG.info("kill process is failure, pid : %s"%pid)
       return -1
    return 1

